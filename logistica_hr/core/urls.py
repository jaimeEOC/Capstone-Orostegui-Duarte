"""
URLs de la aplicación core
"""

from django.urls import path
from . import views

# app_name = 'core'  # Comentado para evitar conflictos de namespace

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),  # Página principal
    path('employees/', views.employees_list, name='employees_list'),  # Lista de empleados
    path('tasks/', views.tasks_list, name='tasks_list'),  # Lista de tareas
    path('performance/', views.performance_dashboard, name='performance_dashboard'),  # Dashboard de rendimiento
    path('reports/', views.reports_list, name='reports_list'),  # Lista de reportes
    
    # API endpoints
    path('api/v1/', views.api_root, name='api-root'),  # API root
    path('api/v1/health/', views.health_check, name='health-check'),
]
