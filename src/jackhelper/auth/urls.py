from django.urls import path

from .views import *


urlpatterns = [
    path('', auth, name='auth'),
    path('login/', login),
]