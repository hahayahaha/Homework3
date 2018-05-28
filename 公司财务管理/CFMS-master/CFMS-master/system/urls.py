from django.conf.urls import url
from system import views

urlpatterns = [
    url(r'^index/$', views.index),
    url(r'^login/$',views.login),
    url(r'^register/$', views.register),
    url(r'^journal/$', views.Journalizing),
    url(r'^confirm/$',views.user_register_confirm),
]