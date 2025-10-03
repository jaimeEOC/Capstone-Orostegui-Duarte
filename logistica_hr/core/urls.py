"""
URLs de la aplicación core
"""

from django.urls import path
from . import views

# app_name = 'core'  # Comentado para evitar conflictos de namespace

urlpatterns = [
    # Páginas principales
    path('', views.home_view, name='home'),  # Página principal
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # Páginas de error y acceso
    path('access-denied/', views.access_denied_view, name='access_denied'),
    
    # Páginas de contenido (temporalmente comentadas hasta implementar)
    # path('employees/', views.employees_list, name='employees_list'),  # Lista de empleados
    # path('tasks/', views.tasks_list, name='tasks_list'),  # Lista de tareas
    # path('performance/', views.performance_dashboard, name='performance_dashboard'),  # Dashboard de rendimiento
    # path('reports/', views.reports_list, name='reports_list'),  # Lista de reportes
    
    # API endpoints (temporalmente comentadas hasta implementar)
    # path('api/v1/', views.api_root, name='api-root'),  # API root
    # path('api/v1/health/', views.health_check, name='health-check'),
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
