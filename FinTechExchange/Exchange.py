# -*- coding: utf-8 -*-
"""
Created on Fri May  4 14:19:38 2018

@author: xy
"""

import datetime


# order应该具有流水号，交易者ID，买入或卖出， 价格， 数量 ，时间， 股票代码这些参数
class Order:

    def __init__(self, number, tid, otype, price, qty, time, stockcode):
        self.tid = tid
        self.otype = otype
        self.price = price
        self.qty = qty
        self.time = time
        self.number = number
        self.stockcode = stockcode

    def __str__(self):
        return '[%s %s %s %s P=%03d Q=%s T=%5.2f]' % (self.number, self.tid, self.stc, self.otype, self.price, self.qty, self.time)

    def decrease_qty(self, qty):
        self.qty -= qty


class Orderbook_half:
    
    def __init__(self, booktype, worstprice):
        # booktype: bids or asks?
        self.booktype = booktype
        # dictionary of orders received, indexed by number
        self.orders = {}
        # limit order book, dictionary indexed by price, with order info
        self.lob = {}
        # anonymized LOB, lists, with only price/qty info
        self.lob_anon = []
        # summary stats
        self.best_price = worstprice
        self.best_number = None
        self.worstprice = worstprice
        self.n_orders = 0  # how many orders?
        self.lob_depth = 0  # how many different prices on lob?
    
    def anonymize_lob(self):
        #生成一个排序后的只含有价格和数量的order列表
        self.lob_anon=[]
        for price in sorted(self.lob):
            self.lob_anon.append([price, self.lob[price][0]])
        
    def build_lob(self):
        #生成订单字典，键为price, 值为Order中有用的信息
        #并生成相应的anonymize_lob， 找出best price
        self.lob = {}
        for number in self.orders:
            order = self.orders[number]
            price = order.price
            if price in self.lob:
                self.lob[price][0] += order.qty
                self.lob[price][1].append([order.tid, order.qty, order.time, order.number])
            else:
                #新生成键值对，值为一个list(或者是元组)，list中有所有order的quantity的和与order list
                self.lob[price] = [order.qty, [[order.tid, order.qty, order.time, order.number]]]
        self.anonymize_lob()
        self.best_order()
    
    def book_add(self, order):
        #新增order
        self.orders[order.number] = order
        self.n_orders += 1
        self.build_lob()
        
    def book_del(self, ordernumber):
        #删除order
        if ordernumber in self.orders:
            del(self.orders[ordernumber])
            self.build_lob()
    
    def best_order(self):
        #找出最优的price和order
        self.lob_depth = len(self.lob_anon)
        if self.lob_depth > 0 :
            if self.booktype == 'bid':
                self.best_price = self.lob_anon[-1][0]
            else :
                self.best_price = self.lob_anon[0][0]
            self.best_number = self.lob[self.best_price][1][0][3]
        else :
            self.best_price = self.worstprice
            self.best_number = None
    
    def return_order(self, number):
        #查找某个特定的order
        return self.orders[number]
    
    def decrease_order_qty(self, number, qty):
        #交易中减少其中某个order的量
        self.orders[number].decrease_qty(qty)
        self.build_lob()
    
    def reset(self):
        #重置，即清空所有数据
        self.orders={}
        self.build_lob()
  
          
class Orderbook():

    def __init__(self, sys_minprice, sys_maxprice, stockcode):
        #由bid book和ask order构成，并增加一个stockcode用于限制交易的股票
        self.bids = Orderbook_half('bid', sys_minprice)
        self.asks = Orderbook_half('ask', sys_maxprice)
        self.stockcode = stockcode
        
class Exchange(Orderbook):
    #交易类
    
    def __init__(self, sys_minprice, sys_maxprice, stockcode, initprice):
        #初始化交易
        super().__init__(sys_minprice, sys_maxprice, stockcode)
        self.tape = []
        self.orderlist=[]#仅在集合竞价中用于保存所有的order,其他阶段保持空的状态
        self.price = initprice #显示当前价格，用于更新stock数据
        self.per_qty = 0#当前交易量，用于更新stock数据
        self.doneorder={}#根据成交记录生成一个order，这些order用于更新trader数据
    
    def orderlist_dec(self,order):
        #用于集合竞价中的撤单操作
        self.orderlist.remove(order)
        return self.process_order_A(datetime.datetime.now())
    
    def save_orderlist(self):
        #从连续竞价到集合竞价，保存已有的order
        for num in self.bids.orders:
            self.orderlist.append(self.bids.orders[num])
        for num in self.asks.orders:
            self.orderlist.append(self.asks.orders[num])
    
    def reset(self):
        #清空数据
        self.asks.reset()
        self.bids.reset()
        self.per_qty = 0
        self.doneorder={}
        
    def add_order(self, order):
        #向系统中增加一个order, market中不应该直接使用该函数
        if order.otype == 'bid':
            self.bids.book_add(order)
        else:
            self.asks.book_add(order)
    
    def delete_order(self, order):
        #删除order, trader撤单直接delete_order即可
        if order.otype == 'bid':
            self.bids.book_del(order.number)
        else:
            self.asks.book_del(order.number)
    
    def delete_order_by_num(self,number):
        #与上一个函数相似，为了在后续的交易过程中简化处理，特意增加该方法
        self.bids.book_del(number)
        self.asks.book_del(number)
        
            
    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self, time, verbose):
        public_data = {}
        public_data['time'] = time
        public_data['bids'] = {'best':self.bids.best_price,
                               'worst':self.bids.worstprice,
                               'n': self.bids.n_orders,
                               'lob':self.bids.lob_anon}
        public_data['asks'] = {'best':self.asks.best_price,
                               'worst':self.asks.worstprice,
                               'n': self.asks.n_orders,
                               'lob':self.asks.lob_anon}
        if verbose:
            print('publish_lob: t=%d' % time)
            print('BID_lob=%s' % public_data['bids']['lob'])
            print('ASK_lob=%s' % public_data['asks']['lob'])
        return public_data
    
    
    def tape_dump(self, fname, fmode, tmode):
        #输出成交记录
        dumpfile = open(fname, fmode)
        for tapeitem in self.tape:
            dumpfile.write('%s, %s\n' % (tapeitem['time'], tapeitem['price']))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []
      
    def return_doneorder(self):
        #返回所有生成的当前已成交order 
        return self.doneorder      
        
    def save_record(self, time, price, qty, bidid, askid, bidnumber, asknumber):
        #保存每次交易的记录
        record = {'time':time,
                  'price':price,
                  'quantity':qty,
                  'bid_id':bidid,
                  'ask_id':askid,
                  'bid_number':bidnumber,
                  'ask_number':asknumber}
        self.doneorder[bidnumber] = Order(bidnumber,bidid,'bid',price,qty,time,self.stockcode)
        self.doneorder[asknumber] = Order(asknumber,askid,'ask',price,qty,time,self.stockcode)
        self.tape.append(record)
        
    def save_record_A(self,time,price,quantity,otype,tid,number):
        #集合竞价中保存交易记录，该方法目的为简化代码
        record = {'time':time,
                  'price':price,
                  'quantity':quantity,
                  'type':otype,
                  'id':tid,
                  'number':number}
        self.doneorder[number] = Order(number,tid,otype,price,quantity,time,self.stockcode)
        self.tape.append(record)
    
    def process_order_A(self, time, neworder = None, finish = False):
        #集合竞价, 竞价结束之前不断加入order，但是不成交，只输出成交价格, finish = True时该阶段结束
        #收盘集合竞价之前需要将已有的order存入orderlist中，且此时不能撤单
        if len(self.orderlist) == 0:
            self.save_orderlist()
        #先得到仅含price 和 quantity 的anonymize_lob
        self.reset()
        if neworder != None:
            #保证在该阶段结束时能通过此方法完成交易, neworder初始化为None
            self.orderlist.append(neworder)
        for order in self.orderlist:
            self.add_order(order)
        #确定使得 成交量最大 的成交价格
        #总成交量为sumqty
        sumqty = 0
        price = self.asks.best_price
        while self.bids.best_price >= self.asks.best_price and(self.bids.n_orders !=0 and self.asks.best_price != 0):
            bid_order = self.bids.lob[self.bids.best_price][1][0]
            ask_order = self.asks.lob[self.asks.best_price][1][0]
            #按照价格优先和时间优先原则选出相应的买方和卖方order，交易掉其中较小的
            if bid_order[1] > ask_order[1]:
                sumqty += ask_order[1]
                price = self.asks.best_price
                self.asks.book_del(ask_order[3])
                self.bids.decrease_order_qty(bid_order[3], ask_order[1])  
            elif bid_order[1] < ask_order[1]:
                sumqty += bid_order[1]
                price = self.bids.best_price
                self.bids.book_del(bid_order[3])
                self.asks.decrease_order_qty(ask_order[3], bid_order[1])
            else:
                sumqty += bid_order[1]
                price = self.bids.best_price
                self.bids.book_del(bid_order[3])
                self.asks.book_del(ask_order[3])
        #交易完后，再一次修正price，使得最终所有大于price的bid均交易掉，小于price的ask均交易掉
        if price < self.bids.best_price:
            price = self.bids.best_price
        if price > self.asks.best_price:
            price = self.asks.best_price
        if finish == True:
            #保存集合竞价的交易结果
            #用于处理等于price的order
            orderbid=[sumqty,[]]
            orderask=[sumqty,[]]  
            #用order列表的第一项来保存等于price的order中发生了交易的quantity
            for order in self.orderlist:
                if order.otype == 'bid' and order.price > price:
                    orderbid[0] -= order.qty
                    self.save_record_A(time,price,order.qty,'bid',order.tid,order.number)
                elif order.otype == 'ask' and order.price < price:
                    orderask[0] -= order.qty
                    self.save_record_A(time,price,order.qty,'ask',order.tid,order.number)
                elif order.price == price:
                    if order.otype == 'bid':
                        orderbid[1].append(order)
                    else:
                        orderask[1].append(order)
            #等于price的order中交易量为allqty
            for ask_order in orderask[1]:
                if orderask[0] <= 0:
                    break
                if orderask[0] <= ask_order.qty:
                    self.save_record_A(time,price,orderask[0],'ask',ask_order.tid,ask_order.number)
                    break
                self.save_record_A(time,price,ask_order.qty,'ask',ask_order.tid,ask_order.number)
                orderask[0] -= ask_order.qty
            for bid_order in orderbid[1]:
                if orderbid[0] <= 0:
                    break
                if orderbid[0] <= bid_order.qty:
                    self.save_record_A(time,price,orderbid[0],'bid',bid_order.tid,bid_order.number)
                    break
                self.save_record_A(time,price,bid_order.qty,'bid',bid_order.tid,bid_order.number)
                orderbid[0] -= bid_order.qty
            self.orderlist = []
            self.price = price
            self.per_qty = sumqty
        return price
    
    def process_order_B(self, time, order):
        #进行交易，连续竞价
        #先将order加入到orderbook中
        self.doneorder = {}
        self.add_order(order)
        sumqty = 0 #总交易量
        while self.bids.best_price >= self.asks.best_price and(self.bids.n_orders != 0 and self.asks.n_orders != 0):
            #满足需要交易的条件
            best_bid_qty=self.bids.lob[self.bids.best_price][0]
            best_ask_qty=self.asks.lob[self.asks.best_price][0]
            if order.otype == 'bid':
                #新增买方order使得达成交易条件
                for askorder in self.asks.lob[self.asks.best_price][1]:
                    present_qty = askorder[1]
                    if best_bid_qty >= present_qty:
                        #买方数量多于卖方
                        #将买方的order删除，减少quantity后重新 add， 删除当前的ask order
                        self.save_record(time, self.asks.best_price, present_qty, order.tid, askorder[0], order.number, askorder[3])               
                        sumqty += present_qty
                        self.delete_order(order)
                        if best_bid_qty > present_qty:
                            order.decrease_qty(present_qty)
                            self.add_order(order)
                        self.delete_order_by_num(askorder[3])
                        best_bid_qty -= present_qty
                    else:
                        #买方数量小于卖方
                        #删除买方order, 并相应的减少当前ask order中的quantity
                        self.save_record(time, self.asks.best_price, best_bid_qty, order.tid, askorder[0], order.number, askorder[3])
                        sumqty += best_bid_qty
                        self.asks.decrease_order_qty(askorder[3],best_bid_qty)
                        self.delete_order(order)
                        break
            else:
                #新增卖方order使得达成交易条件
                for bidorder in self.bids.lob[self.bids.best_price][1]:
                    present_qty = bidorder[1]
                    if best_ask_qty >= present_qty:
                        #卖方数量小于买方
                        #具体细节处理同上
                        self.save_record(time, self.bids.best_price, present_qty,  bidorder[0],order.tid,  bidorder[3],order.number)               
                        sumqty += present_qty
                        self.delete_order(order)
                        if best_ask_qty > present_qty:
                            order.decrease_qty(present_qty)
                            self.add_order(order)
                        self.delete_order_by_num(bidorder[3])
                        best_ask_qty -= present_qty
                    else:
                        self.save_record(time, self.bids.best_price, best_ask_qty,  bidorder[0],order.tid,  bidorder[3],order.number)
                        sumqty += best_ask_qty
                        self.bids.decrease_order_qty(bidorder[3],best_ask_qty)
                        self.delete_order(order)
                        break
        self.price = self.tape[-1]['price'] 
        self.per_qty = sumqty          
    
    def return_info(self):
        #向外界提供需要的数据，暂时只返回self.price和quantity更新股票价格,和相关anonymize_lob信息
        return [self.price, self.per_qty, self.bids.lob_anon, self.asks.lob_anon]

class Trader:
    #交易者
    
    def  __init__(self, tid, balance, profit, stocks):
        #trader id , 余额，利润， 所拥有的order, 拥有的stock
        self.balance = balance
        self.profit = profit
        self.tid = tid
        self.orders = {}
        self.stocks = stocks #字典 stockcode为键,值为[买入均价，现价,利润，总quantity，总金额]
    
    def __str__(self):
        return '[TID %s balance %s orders %s]' % (self.tid, self.balance, self.orders)
               
    def delete_order(self, number, bidwithdraw = False):
        #删除order，如果是买入撤单则应该增加余额    
        if bidwithdraw == True:
            self.balance += self.orders[number].price * self.orders[number].qty
        del(self.orders[number])
    
    def order_dec(self,number, qty):
        #成交的order只有一部分时,减少该order的quantity, 否则直接删除
        if self.orders[number].qty == qty:
            del(self.orders[number])
        else:
            self.orders[number].decrease_qty(qty)
    
    def carculate_profit(self):
        for stock in self.stocks:
            self.profit += stock[3]
    
    def done_order(self, order):
        #成功交易后改变stock的内容，可以是add也可以是delete
        #order为生成的成功交易的委托
        if order.otype == 'bid':
            if order.stockcode in self.stocks:
                stockinfo = self.stocks[order.stockcode]
                profitchange = stockinfo[3]*(order.price-stockinfo[1])
                self.profit += profitchange
                stockinfo[2] += profitchange
                stockinfo[1] = order.price
                stockinfo[4] += order.qty*order.price + profitchange
                stockinfo[0] = round((stockinfo[0]*stockinfo[3]+order.qty*order.price)/(stockinfo[3]+order.qty),2)
                stockinfo[3] += order.qty
                self.stocks[order.stockcode] = stockinfo
                self.order_dec(order.number, order.qty)
            else:
                stockinfo = [order.price, order.price, 0, order.qty, order.price*order.qty]
                self.stocks[order.stockcode] = stockinfo
                self.order_dec(order.number, order.qty)
        else:
            #卖出
            stockinfo = self.stocks[order.stockcode]
            if stockinfo[3] <= order.qty:
                #实际上小于已在create_order限制不能取到,即此处只有等于，删除该股票及order，增加余额
                del(self.stocks[order.stockcode])
                self.delete_order(order.number)
                self.balance += order.price*order.qty
            else:
                #只卖出了一部分
                self.balance += order.price*order.qty
                stockinfo = self.stocks[order.stockcode]
                profitchange = stockinfo[3]*(order.price - stockinfo[1])
                self.profit += profitchange
                stockinfo[2] += profitchange
                stockinfo[1] = order.price
                stockinfo[4] = stockinfo[4] - order.qty*order.price + profitchange
                stockinfo[0] = round((stockinfo[0]*stockinfo[3]-order.qty*order.price)/(stockinfo[3]-order.qty),2)
                stockinfo[3] -= order.qty
                self.stocks[order.stockcode] = stockinfo
                self.order_dec(order.number, order.qty)
                
    
    
    def update_stock(self,stockcode,price):
        #更新某支股票的现价，并更新self.stocks和收益，这里的price是对应stockcode的stock的市场价格。为了保证交易者的股票的价格和市场的价格是相同的。
        delta_profit=(price-self.stocks[stockcode][1])*self.stocks[stockcode][3]
        #利润的增量
        self.stocks[stockcode][1]=price
        #更新对应的股票的价格
        self.stocks[stockcode][2]=self.stocks[stockcode][2]+delta_profit
        #更新对应的股票的利润
        return
    
    def create_order(self,stock,otype,price,qty):
        #根据余额和stock决定是否能生成委托，更新余额，返回委托
        time=datetime.datetime.now()#委托时间
        number_time=str(time.year)+str(time.month)+str(time.day)+str(time.hour)+str(time.minute)+str(time.second)+str(time.microsecond)
        number=number_time+str(stock.stockcode)+str(self.tid)
        order=Order(number,self.tid,price,qty,time,stock.stockcode)
        #传入Price 注意有价格限制 
        if otype=='bid':
            self.balance-=stock.price*stock.qty
        #改变余额账户，只考虑买股票的情况
        else:
            self.orders[order.number]=order
        #改变订单账户，只考虑卖股票的情况
        return order
    
    
class Stock:
    #股票
    
    def __init__(self, stockcode, price):
        self.stockcode = stockcode
        self.pre_prece = price #昨日收盘价
        self.price = price #现价
        self.volume = 0 #成交量
        self.minprice = round(price*0.9,2) #跌停价
        self.maxprice = round(price*1.1,2) #涨停价
        self.change = 0.00 #涨跌
        self.rate = 0.0000 #涨跌幅
    
    def update(self,price,quantity):
        self.price = price
        self.volume += quantity
        self.change = self.price - self.pre_prece
        self.rate = round(self.change/self.pre_prece, 4)

class Market:
    #市场
    def __init__(self,time1,time2,time3,time4,time5,time6, stocks, traders):
        #time1为开始时间
        #time1~time2为集合竞价阶段1-1，期间可以委托，可以撤单
        #time2~time3为集合竞价阶段1-2，期间只能委托，不能撤单
        #time4~time5为连续竞价阶段
        #time5~time6为集合竞价阶段2，期间不能撤单
        #time6为结束时间
        #stocks为市场上的股票
        #traders为市场上的交易者
        self.time1 = int(time1)
        self.time2 = int(time2)
        self.time3 = int(time3)
        self.time4 = int(time4)
        self.time5 = int(time5)
        self.time6 = int(time6)
        self.stocks = stocks
        self.traders = traders
        self.exchangedic = {}
        
    def add_stock(self, stock):
        self.stocks[stock.stockcode] = stock
    
    def add_trader(self,trader):
        self.traders[trader.tid] = trader
    
    def create_exchange(self):
        self.exchangedic = {}
        for stock in self.stocks:
            self.exchangedic[stock.stockcode] = Exchange(stock.minprice, stock.maxprice, stock.stockcode, stock.price)
        
    def return_stage(self):
        #根据当前时间返回当前的阶段
        #1为集合竞价1-1,2为集合竞价1-2,3为连续竞价，4为集合竞价2, 5表示休市
        time = datetime.datetime.now()
        #提取出h,m,s转换为int
        nowtime=time.hour*10000+time.minute*100+time.second
        if self.time1 <= nowtime and nowtime <= self.time2:
            return 1
        elif self.time2 < nowtime and nowtime <=self.time3:
            return 2
        elif self.time4 <= nowtime and nowtime <=self.time5:
            return 3
        elif self.time5 < nowtime and nowtime <=self.time6:
            return 4
        else:
            return 5
    
    def withdrawal(self,order):
        #撤单
        stage = self.return_stage()
        bidwithdraw = False
        if order.otype == 'bid':
            bidwithdraw = True
        if stage == 1:
            price=self.exchangedic[order.stockcode].orderlist_dec(order)
            print(price)#显示当前集合竞价的交易价格
            self.traders[order.tid].delete_order(order.number, bidwithdraw)
        elif stage == 3:
            self.exchangedic[order.stockcode].delete_order(order.number)
            self.traders[order.tid].delete_order(order.number, bidwithdraw)
        elif stage == 2 or stage ==4:
            print('当前集合竞价不允许撤单')
        else:
            print('市场关闭')
        
    def add_order(self,order):
        #增加委托
        time = datetime.datetime.now()
        stage = self.return_stage()
        if stage == 1 or stage == 2 or stage == 4:
            price=self.exchangedic[order.stockcode].process_order_A(time, order)
            print(price)#显示当前集合竞价的交易价格
        elif stage == 3:
            self.exchangedic[order.stockcode].process_order_B(time, order)
            newinfo = self.exchangedic[order.stockcode].return_info()
            doneorder = self.exchangedic[order.stockcode].return_doneorder()
            for number in doneorder:
                self.traders[doneorder[number].tid].done_order(doneorder[number])
            self.stocks[order.stockcode].update(newinfo[0],newinfo[1])
        else:
            print('市场关闭')
            
    def save_orderlist(self):
        #用于在连续竞价过度到集合竞价时保存已有的委托数据
        for stockcode in self.exchangedic:
            self.exchangedic[stockcode].save_orderlist()
    
    def finish_A(self):
        #用于在集合竞价结束时完成所有的交易
        time = datetime.datetime.now()
        for stockcode in self.exchangedic:
            self.exchangedic[stockcode].process_order_A(time=time, finish = True)
            newinfo = self.exchangedic[stockcode].return_info()
            doneorder = self.exchangedic[stockcode].return_doneorder()
            for number in doneorder:
                self.traders[doneorder[number].tid].done_order(doneorder[number])
            self.stocks[stockcode].update(newinfo[0],newinfo[1])
    
    def update_trader_stock(self,tid):
        #根据市场上各股票的价格更新市场上某一个trader的持仓及收益
        for stockcode in self.traders[tid].stocks:
            newinfo = self.exchangedic[stockcode].return_info()
            self.traders[tid].update_stock(stockcode, newinfo[0])
        
        
        
        
if __name__=='__main__':
    """
    #测试集合竞价代码
    exchange = Exchange(0,100,'001')
    orderlist=[]
    for i in range(10):
        order1=Order(str(i),'1','bid',round(12+0.02*i,2),i,str(i),'001')
        order2=Order(str(i+10),'2','ask',round(12.24-0.02*i,2),i,str(i),'001')
        orderlist.append(order1) 
        orderlist.append(order2)
    result1=exchange.process_order_A('2018-5-17',orderlist,True)
    result2=exchange.tape
    """
    """
    exchange = Exchange(0,100,'101')
    for i in range(10):
        order1=Order(str(i),'1','bid',round(12+0.02*i,2),i,str(i),'001')
        order2=Order(str(i+10),'2','ask',round(12.24-0.02*i,2),i,str(i),'001')
        exchange.process_order_B('2018-5-17',order1)
        exchange.process_order_B('2018-5-17',order2)
    result2=exchange.tape
    """
        
    
    