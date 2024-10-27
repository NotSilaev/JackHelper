from django.urls import path

from .views import *
from .api import *


urlpatterns = [
    path('', orders, name='orders'),

    path('api/getOrders/', getOrders, name='getOrders'),
]