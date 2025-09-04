"""
URLs para la aplicación users
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
# router.register(r'', views.UserViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    path('', include(router.urls)),
]
