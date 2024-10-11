from django.urls import path

from .views import *
from .api import *


urlpatterns = [
    path('', stats, name='stats'),

    path('api/getStatsBlock/', getStatsBlock, name='get_stats_block')
]