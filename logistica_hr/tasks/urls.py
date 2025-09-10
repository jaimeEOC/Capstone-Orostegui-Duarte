"""
URLs para la aplicación tasks
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tasks'

router = DefaultRouter()
# router.register(r'', views.TaskViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    path('', include(router.urls)),
]




