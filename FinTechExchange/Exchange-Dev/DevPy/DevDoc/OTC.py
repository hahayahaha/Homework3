# -*- coding: utf-8 -*-
"""
Created on Sat May 26 16:15:10 2018

@author: xiaoyang
"""

import datetime


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
        return '[%s %s P=%.2f Q=%s]' % (self.tid, self.stockcode, self.price, self.qty)
    
class OTC_market:
    
    def __init__(self, traders, orders):
        self.traders = traders
        self.bidorders = {}
        self.askorders = {}
        for number in orders:
            if orders[number].otype == 'bid':
                self.bidorders[number] = orders[number]
            else:
                self.askorders[number] = orders[number]
        
    def add_trader(self,trader):
        self.traders[trader.tid] = trader
    
    def delete_trader(self,trader):
        del(self.traders[trader.tid])
        
    def add_order(self,order):
        if order.otype == 'bid':    
            self.bidorders[order.number] = order
        else:
            self.askorders[order.number] = order   
    
    def show_orders(self, otype):
        #otype决定显示买方order还是卖方order
        s=''
        if otype == 'bid':
            for number in self.bidorders:
                s = s + self.bidorders[number]
        else:
            for number in self.askorders:
                s = s + self.askorders[number]
        return s
    
    def b_a_click(self, otype, tid, chosenorder):
        #用户选中某委托， 如果能成交，则根据成交结果更新traders和orders
        if otype == 'bid':
            result = self.traders[tid].exchange(otype,chosenorder.price,chosenorder.qty,chosenorder.stockcode)
            if result == True:
                #能成交
                self.traders[chosenorder.tid].done_order(chosenorder)
                del(self.askorders[chosenorder.number])
            else:
                print('余额不足')
        else:
            result = self.traders[tid].exchange(otype,chosenorder.price,chosenorder.qty,chosenorder.stockcode)
            if result == True:
                self.traders[chosenorder.tid].done_order(chosenorder)
                del(self.bidorders[chosenorder.number])
            else:
                print('持仓不足')
                
    def withdraw(self, order):
        #撤单
        self.traders[order.tid].delete_order(order)
        if order.otype == 'bid':
            del(self.bidorders[order.number])
        else:
            del(self.askorders[order.number])
    
    
class Trader:
    
    def __init__(self, tid, balance, stocks, orders):
        #trader id，余额，持股：键为stockcode,值为持仓，这里不排斥持仓为0的情况
        self.tid = tid
        self.balance = balance
        self.orders = orders
        self.stocks = stocks
        
    def exchange(self, otype, price, quantity, stockcode):
        #选中委托直接交易，更新trader信息, 如果不能进行交易则返回False，否则返回True
        if otype == 'bid':
            if price*quantity > self.balance:
                return False
            else:
                self.balance -= price*quantity
                if stockcode in self.stocks:
                    self.stocks[stockcode] += quantity
                else:
                    self.stocks[stockcode] = quantity
        else:
            if stockcode not in self.stocks:
                return False
            elif self.stocks[stockcode] < quantity:
                return False
            else:
                self.balance += price*quantity
                self.stocks[stockcode] -= quantity
        return True
    
    def create_order(self, otype, stockcode):
        if otype == 'bid':
            price = float(input('输入委托价格:'))
            quantity = int(input('输入委托数量（限制整数）:'))
            while price*quantity > self.balance:
                print('余额不足,请重新输入：')
                price = float(input('输入委托价格:'))
                quantity = int(input('输入委托数量（限制整数）:'))
            self.balance -= price*quantity
        else:
            if stockcode not in self.stocks:
                print('无持仓，无法卖出')
                return None
            price = float(input('输入委托价格:'))
            quantity = int(input('输入委托数量（限制整数）:'))
            while quantity > self.stocks[stockcode]:
                quantity = int(input('数量超过持仓，从新输入数量：'))
            self.stocks[stockcode] -= quantity
        time=datetime.datetime.now()#委托时间
        number_time=str(time.year)+str(time.month)+str(time.day)+str(time.hour)+str(time.minute)+str(time.second)+str(time.microsecond)
        number=number_time+str(stockcode)+str(self.tid)
        order=Order(number,self.tid,otype,price,quantity,time,stockcode)
        return order
    
    def done_order(self, order):
        #委托成交
        del(self.orders[order.number])
        if order.otype == 'bid':
            if order.stockcode in self.stocks:
                self.stocks[order.stockcode] += order.qty
            else:
                self.stocks[order.stockcode] = order.qty
        else:
            self.balance += order.price*order.qty
    
    def delete_order(self, order):
        #撤单
        if order.otype == 'bid':
            self.balance += order.price*order.qty
        else:
            self.stocks[order.stockcode] += order.qty
        del(self.orders[order.number])
