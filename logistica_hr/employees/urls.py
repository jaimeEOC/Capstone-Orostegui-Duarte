"""
URLs para la aplicación employees
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'employees'

router = DefaultRouter()
# router.register(r'', views.EmployeeViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    path('', include(router.urls)),
]


