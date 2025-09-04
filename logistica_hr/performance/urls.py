"""
URLs para la aplicación performance
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'performance'

router = DefaultRouter()
# router.register(r'', views.PerformanceViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    path('', include(router.urls)),
]


