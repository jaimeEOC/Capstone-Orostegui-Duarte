"""
URLs para la aplicación reports
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

router = DefaultRouter()
# router.register(r'', views.ReportViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    path('', include(router.urls)),
]


