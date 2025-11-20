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
    
    # Admin - Gestión de empleados
    path('admin/employees/', views.admin_employees_list, name='admin_employees_list'),
    path('admin/employees/<int:employee_id>/assign-supervisor/', views.admin_assign_supervisor, name='admin_assign_supervisor'),
    path('admin/employees/<int:employee_id>/edit/', views.admin_edit_employee, name='admin_edit_employee'),
    path('admin/employees/<int:employee_id>/delete/', views.admin_delete_employee, name='admin_delete_employee'),
    path('admin/supervisors/<int:supervisor_id>/edit/', views.admin_edit_supervisor, name='admin_edit_supervisor'),
    path('admin/supervisors/<int:supervisor_id>/delete/', views.admin_delete_supervisor, name='admin_delete_supervisor'),
    
    # Supervisor - Gestión de equipo
    path('supervisor/employees/', views.supervisor_employees_list, name='supervisor_employees_list'),
    path('supervisor/reports/', views.supervisor_team_reports, name='supervisor_team_reports'),
    path('supervisor/evaluate/', views.supervisor_evaluate_performance, name='supervisor_evaluate_performance'),
    path('supervisor/evaluate/<int:employee_id>/', views.supervisor_evaluate_performance, name='supervisor_evaluate_employee'),
    
    # API endpoints
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
