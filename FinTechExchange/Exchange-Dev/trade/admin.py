from django.contrib import admin

from .models import Stock, Order, UserStock, StockPrice

admin.site.register(Stock)
admin.site.register(Order)
admin.site.register(UserStock)
admin.site.register(StockPrice)
# Register your models here.
