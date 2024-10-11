from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('auth/', include('auth.urls')),
    path('stats/', include('stats.urls')),
]
