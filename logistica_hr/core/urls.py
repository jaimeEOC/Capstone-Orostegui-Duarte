"""
URLs de la aplicación core
"""

from django.urls import path
from . import views

# app_name = 'core'  # Comentado para evitar conflictos de namespace

urlpatterns = [
    # Páginas principales
    path('', views.home_view, name='home'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # Páginas de error y acceso
    path('access-denied/', views.access_denied_view, name='access_denied'),
    
    # API endpoints
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
