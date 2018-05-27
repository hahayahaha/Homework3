# -*- coding: utf-8 -*-
"""
Created on Fri May  4 14:19:38 2018

@author: xy
"""

# order应该具有流水号，交易者ID，买入或卖出， 价格， 数量 ，时间， 股票代码这些参数
class Order:

    def __init__(self, number, tid, otype, price, qty, time, stockcode):
        self.tid = tid
        self.otype = otype
        self.price = price
        self.qty = qty
        self.time = time
        self.number = number
        self.stc = stockcode

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
            if self.booktype == 'Bid':
                self.best_price = self.lob_anon[-1][0]
            else :
                self.best_price = self.lob_anon[0][0]
            self.best_number = self.lob[self.best_price][1][0][3]
        else :
            self.best_price = self.worstprice
            self.best_tid = None
    
    def return_order(self, number):
        #查找某个特定的order
        return self.orders[number]
    
    def decrease_order_qty(self, number, qty):
        #交易中减少其中某个order的量
        self.orders[number].decrease_qty(qty)
        self.build_lob()
  
          
class Orderbook():

    def __init__(self, sys_minprice, sys_maxprice, stockcode):
        #由bid book和ask order构成，并增加一个stockcode用于限制交易的股票
        self.bids = Orderbook_half('Bid', sys_minprice)
        self.asks = Orderbook_half('Ask', sys_maxprice)
        self.stockcode = stockcode
        
class Exchange(Orderbook):
    #交易类
    
    def __init__(self, sys_minprice, sys_maxprice, stockcode):
        #初始化交易
        super().__init__(sys_minprice, sys_maxprice, stockcode)
        self.tape = []
        
    def add_order(self, order):
        #向系统中增加一个order
        if order.otype == 'Bid':
            self.bids.book_add(order)
        else:
            self.asks.book_add(order)
    
    def delete_order(self, order):
        #删除order
        if order.otype == 'Bid':
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
      
    def save_record(self, time, price, qty, bidid, askid, bidnumber, asknumber):
        #保存每次交易的记录
        record = {'time':time,
                  'price':price,
                  'quantity':qty,
                  'bid_id':bidid,
                  'ask_id':askid,
                  'bid_number':bidnumber,
                  'ask_number':asknumber}
        self.tape.append(record)
        
    def process_order_A(self, time, orderlist):
        #集合竞价
        return
    
    def process_order_B(self, time, order):
        #进行交易，连续竞价
        #先将order加入到orderbook中
        self.add_order(order)
        while self.bids.best_price >= self.asks.best_price and(self.bids.n_orders != 0 or self.asks.n_orders != 0):
            #满足需要交易的条件
            best_bid_qty=self.bids.lob[self.bids.best_price][0]
            best_ask_qty=self.asks.lob[self.asks.best_price][0]
            if order.otype == 'Bid':
                #新增买方order使得达成交易条件
                for askorder in self.asks.lob[self.asks.best_price][1]:
                    present_qty = askorder[1]
                    if best_bid_qty >= present_qty:
                        #买方数量多于卖方
                        #将买方的order删除，减少quantity后重新 add， 删除当前的ask order
                        self.save_record(time, self.asks.best_price, present_qty, order.tid, askorder[0], order.number, askorder[3])               
                        self.delete_order(order)
                        if best_bid_qty > present_qty:
                            order.decrease_qty(present_qty)
                            self.add_order(order)
                        self.delete_order(askorder[3])
                        best_bid_qty -= present_qty
                    else:
                        #买方数量小于卖方
                        #删除买方order, 并相应的减少当前ask order中的quantity
                        self.save_record(time, self.asks.best_price, best_bid_qty, order.tid, askorder[0], order.number, askorder[3])
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
                        self.delete_order(order)
                        if best_ask_qty > present_qty:
                            order.decrease_qty(present_qty)
                            self.add_order(order)
                        self.delete_order(bidorder[3])
                        best_ask_qty -= present_qty
                    else:
                        self.save_record(time, self.bids.best_price, best_ask_qty,  bidorder[0],order.tid,  bidorder[3],order.number)
                        self.bids.decrease_order_qty(bidorder[3],best_ask_qty)
                        self.delete_order(order)
                        break
                        
class Trader:
    #交易者
    
    def  __init__(self, tid, balance):
        #trader id , 余额， 所拥有的order, 拥有的stock
        self.balance = balance
        self.tid = tid
        self.orders = []
        self.stocks = []
    
    def __str__(self):
        return '[TID %s balance %s orders %s]' % (self.tid, self.balance, self.orders)
       
    def add_order(self, order):
        self.orders.append(order)
        
    def delete_order(self,order):
        self.orders.remove(order)
        
    