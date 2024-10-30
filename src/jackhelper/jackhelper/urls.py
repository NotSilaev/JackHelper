from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('auth/', include('auth.urls')),
    path('stats/', include('stats.urls')),
    path('plans/', include('plans.urls')),
    path('orders/', include('orders.urls')),
]

handler404 = 'main.views.custom_404'