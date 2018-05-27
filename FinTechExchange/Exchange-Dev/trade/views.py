from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core import serializers

from .models import Stock, Order, StockPrice
from user.models import UserProfile


# Create your views here.
order_type = {
    'BUY': 1,
    'SELL': 2
}
status = {
    'UNFINISHED': 1,
    'FINISHED': 2
}

def Index(request):
    # stock = Stock.objects.get(stock_code=1001)
    # stock = get_object_or_404(Stock, stock_code=1001)
    # print(stock)
    # context = {'stock': stock, 'buyer': stock.buyer}
    # order = Order.objects.get(pk=1)
    # print(order.buyer)
    # print(order.price)
    # context = {'stock': order, 'buyer': order.buyer}
    # return render(request, "test.html", context)
    user = UserProfile.objects.get(pk=1)

    print(user.buyer.all())

    return render(request, "trade.html")


def StockView(request, stock_code=1001):
    stocks = Stock.objects.all()
    current_stock = get_object_or_404(Stock, stock_code=stock_code)
    buy_orders = current_stock.orders.filter(type=order_type['BUY'], status=status['UNFINISHED'])
    sell_orders = current_stock.orders.filter(type=order_type['SELL'], status=status['UNFINISHED'])
    print(sell_orders)
    trade_history = current_stock.orders.filter(status=status['FINISHED'])
    context = {
        'stocks': stocks,
        'current_stock': current_stock,
        'buy_orders': buy_orders,
        'sell_orders': sell_orders,
        'trade_history': trade_history,
    }
    return render(request, 'trade.html', context)


def buy(request, stock_code):
    stock = Stock.objects.get(stock_code=stock_code)
    try:
        price = request.POST['price']
        qty = request.POST['qty']
        next_url = request.POST['next']
    except KeyError:
        return HttpResponseRedirect(next_url)

    order = Order(price=price, qty=qty, stock=stock, type=order_type['BUY'], status=status['UNFINISHED'])
    if order.save():
        return HttpResponseRedirect(next_url)
    return HttpResponseRedirect(next_url)


def sell(request, stock_code):
    stock = Stock.objects.get(stock_code=stock_code)
    try:
        price = request.POST['price']
        qty = request.POST['qty']
        next_url = request.POST['next']
    except KeyError:
        return None

    order = Order(price=price, qty=qty, stock=stock, type=order_type['SELL'], status=status['UNFINISHED'])
    print(order.type)
    if order.save():
        return HttpResponseRedirect(next_url)
    return HttpResponseRedirect(next_url)


def getChartData(request, stock_code):
    stock = Stock.objects.get(stock_code=stock_code)
    prices = stock.prices.all()
    serialized_prices = [[price.time, price.price] for price in prices]
    return JsonResponse(serialized_prices, safe=False)