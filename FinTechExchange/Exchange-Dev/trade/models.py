from django.db import models
from user.models import UserProfile

# Create your models here.


class Stock(models.Model):
    stock_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=512)

    @property
    def price(self):
        return 200.12

    def __str__(self):
        return self.name


class Order(models.Model):
    stock = models.ForeignKey(Stock, related_name='orders', on_delete=models.CASCADE)
    buyer = models.ForeignKey(UserProfile, related_name='buy', on_delete=models.CASCADE, blank=True, null=True)
    seller = models.ForeignKey(UserProfile, related_name='sell', on_delete=models.CASCADE, blank=True, null=True)
    type = models.IntegerField()
    status = models.IntegerField()
    price = models.FloatField()
    qty = models.IntegerField()
    publish_time = models.DateTimeField(auto_now_add=True)
    transaction_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class UserStock(models.Model):
    user = models.ForeignKey(UserProfile, related_name='stocks', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, related_name='users', on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'stock')

    @property
    def price(self):
        return 0.3


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, related_name='prices', on_delete=models.CASCADE)
    price = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
