"""
Vistas principales del sistema Logistica HR
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta

from logistica_hr.users.models import User
from logistica_hr.employees.models import Employee, Department
from logistica_hr.tasks.models import Task
from logistica_hr.performance.models import DailyWorkLog, EmployeePerformance


@login_required
def home_view(request):
    """Vista principal que redirige según el rol del usuario"""
    user = request.user
    
    if user.is_admin():
        return admin_dashboard(request)
    elif user.is_supervisor():
        return supervisor_dashboard(request)
    else:
        return employee_dashboard(request)


@login_required
def admin_dashboard(request):
    """Dashboard para administradores"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    
    # Estadísticas de hoy
    today = datetime.now().date()
    today_logs = DailyWorkLog.objects.filter(date=today)
    
    total_packages_today = today_logs.aggregate(
        total=Sum('packages_processed')
    )['total'] or 0
    
    total_trucks_today = today_logs.aggregate(
        total=Sum('trucks_received') + Sum('trucks_dispatched')
    )['total'] or 0
    
    # Empleados activos hoy
    active_employees_today = today_logs.count()
    
    # Departamentos con más empleados
    departments_stats = Department.objects.annotate(
        employee_count=Count('positions__employees')
    ).order_by('-employee_count')[:5]
    
    # Últimas actividades (simulado)
    recent_activities = [
        {'action': 'Nuevo empleado registrado', 'user': 'Juan Pérez', 'time': 'Hace 2 horas'},
        {'action': 'Tarea completada', 'user': 'María González', 'time': 'Hace 3 horas'},
        {'action': 'Reporte generado', 'user': 'Carlos López', 'time': 'Hace 4 horas'},
    ]
    
    context = {
        'user': request.user,
        'stats': {
            'total_users': total_users,
            'total_employees': total_employees,
            'total_departments': total_departments,
            'total_packages_today': total_packages_today,
            'total_trucks_today': total_trucks_today,
            'active_employees_today': active_employees_today,
        },
        'departments_stats': departments_stats,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def supervisor_dashboard(request):
    """Dashboard para supervisores"""
    # Empleados bajo supervisión
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position')
    
    # Estadísticas del equipo
    team_stats = {
        'total_employees': supervised_employees.count(),
        'active_today': DailyWorkLog.objects.filter(
            employee__supervisor=request.user,
            date=datetime.now().date()
        ).count(),
    }
    
    # Tareas pendientes del equipo
    pending_tasks = Task.objects.filter(
        assigned_to__supervisor=request.user,
        status='pending'
    ).select_related('assigned_to__user')[:10]
    
    # Rendimiento del equipo (últimos 7 días)
    week_ago = datetime.now().date() - timedelta(days=7)
    team_performance = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=week_ago
    ).aggregate(
        avg_packages=Avg('packages_processed'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents')
    )
    
    context = {
        'user': request.user,
        'supervised_employees': supervised_employees,
        'team_stats': team_stats,
        'pending_tasks': pending_tasks,
        'team_performance': team_performance,
    }
    
    return render(request, 'supervisor/dashboard.html', context)


@login_required
def employee_dashboard(request):
    """Dashboard para empleados"""
    try:
        employee = request.user.employee_profile
    except:
        employee = None
    
    if not employee:
        context = {
            'user': request.user,
            'error': 'No se encontró perfil de empleado asociado a tu cuenta.'
        }
        return render(request, 'employee/dashboard.html', context)
    
    # Estadísticas personales
    today = datetime.now().date()
    today_log = DailyWorkLog.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    # Tareas asignadas
    my_tasks = Task.objects.filter(
        assigned_to=employee
    ).order_by('-created_at')[:10]
    
    # Rendimiento de la semana
    week_ago = today - timedelta(days=7)
    week_performance = DailyWorkLog.objects.filter(
        employee=employee,
        date__gte=week_ago
    ).aggregate(
        total_packages=Sum('packages_processed'),
        total_trucks=Sum('trucks_received') + Sum('trucks_dispatched'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents')
    )
    
    # Historial de rendimiento (últimos 7 días)
    performance_history = DailyWorkLog.objects.filter(
        employee=employee,
        date__gte=week_ago
    ).order_by('date')
    
    context = {
        'user': request.user,
        'employee': employee,
        'today_log': today_log,
        'my_tasks': my_tasks,
        'week_performance': week_performance,
        'performance_history': performance_history,
    }
    
    return render(request, 'employee/dashboard.html', context)


def access_denied_view(request):
    """Vista para mostrar página de acceso restringido"""
    return render(request, 'auth/access_denied.html', {
        'user': request.user if request.user.is_authenticated else None
    })


@login_required
def api_dashboard_stats(request):
    """API endpoint para estadísticas del dashboard"""
    user = request.user
    
    if user.is_admin():
        stats = {
            'total_users': User.objects.count(),
            'total_employees': Employee.objects.count(),
            'active_today': DailyWorkLog.objects.filter(
                date=datetime.now().date()
            ).count(),
        }
    elif user.is_supervisor():
        stats = {
            'team_employees': Employee.objects.filter(
                supervisor=request.user
            ).count(),
            'active_today': DailyWorkLog.objects.filter(
                employee__supervisor=request.user,
                date=datetime.now().date()
            ).count(),
        }
    else:
        try:
            employee = request.user.employee_profile
            stats = {
                'my_tasks_pending': Task.objects.filter(
                    assigned_to=employee,
                    status='pending'
                ).count(),
                'my_tasks_completed': Task.objects.filter(
                    assigned_to=employee,
                    status='completed'
                ).count(),
            }
        except:
            stats = {}
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })