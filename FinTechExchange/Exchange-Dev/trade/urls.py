from django.urls import path

from . import views

app_name = 'trade'

urlpatterns = [
    path('', views.Index, name='trade-index'),
    path('<int:stock_code>/', views.StockView, name='trade-stock'),
    path('<int:stock_code>/buy/', views.buy, name='buy'),
    path('<int:stock_code>/sell/', views.sell, name='sell'),
    path('<int:stock_code>/chart_data/', views.getChartData, name='chart-data')
    # path('trade/<int:id>', views.stock, name='trade-stock'),
]