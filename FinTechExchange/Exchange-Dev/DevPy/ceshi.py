# -*- coding: utf-8 -*-
"""
Created on Sun May 27 00:04:15 2018

@author: xiaoyang
"""

from exchange import Market,Robot1,Robot2,Stock
import time
import datetime

if __name__=='__main__':
    #对整个market进行测试，随机交易
    #注意输入的时间
    begin = 215400    
    market = Market(begin,begin+100,begin+130,begin+200,begin+300,begin+400,{},{})
    market.create_exchange()
    #十支股票
    for i in range(10):
        stock = Stock('00000%d'%(i+1),5+i*5)
        market.add_stock(stock)
    #10个随机robot1,有钱500000,无持股
    for i in range(10):
        trader = Robot1(str(i),100000,0,{})
        market.add_trader(trader)
    #10个随机robot1,有钱20000，有持仓，每支股票持股1000
    for j in range(10):
        stocks = {}
        for i in range(10):
            stocks['00000%d'%(i+1)] = [5+i*5, 5+i*5, 0, 1000, 5000+5000*i, 1000]
        trader = Robot1(str(j+10), 20000, 0, stocks)
        market.add_trader(trader)
    #4个随机robot2，数据同上
    for i in range(2):
        trader = Robot2(str(i+20),100000,0,{})
        market.add_trader(trader)
    for j in range(2):
        stocks = {}
        for i in range(10):
            stocks['00000%d'%(i+1)] = [5+i*5, 5+i*5, 0, 1000, 5000+5000*i, 1000]
        trader = Robot2(str(j+22), 20000, 0, stocks)
        market.add_trader(trader)
    #随机机器人3，暂无
    #进行随机交易
    #3秒一周期，第一类机器人在第一秒同时操作，操作有[撤单，新增委托]两种，随机选择一个
    #第二类机器人在第二秒同时操作，只有新增委托操作
    #第三类机器人时间为第三秒，每一阶段持续一分钟
    while True:
        now = datetime.datetime.now()
        if now.hour*10000+now.minute*100+now.second > int(begin+400):
            market.finish_A()
            break
        elif now.hour*10000+now.minute*100+now.second > int(begin+130) and now.hour*10000+now.minute*100+now.second <int(begin+132):
            market.finish_A()
        elif now.hour*10000+now.minute*100+now.second < int(begin):
            continue
        for i in range(20):
            stocks = {}
            for stockcode in market.stocks:
                stock = market.stocks[stockcode]
                stocks[stockcode] = [stock.price, stock.maxprice, stock.minprice] 
            order = market.traders[str(i)].strategy(stocks)
            market.add_order(order)
        time.sleep(1)
        
        for i in range(4):
            stocks = {}
            for stockcode in market.stocks:
                stock = market.stocks[stockcode]
                stocks[stockcode] = [stock.price, stock.maxprice, stock.minprice] 
            order = market.traders[str(i+20)].strategy(stocks)
            market.add_order(order)
        time.sleep(1)
        time.sleep(1)
    
    market.show_results()
    for tid in market.traders:
        market.update_trader_stock(tid)
        
        