"""
Vistas principales del sistema Logistica HR
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, timedelta, date

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
    today = datetime.now().date()
    
    # Empleados bajo supervisión con información de estado
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position', 'position__department')
    
    # Agregar información de estado y rendimiento a cada empleado
    employees_with_status = []
    for employee in supervised_employees:
        # Verificar si tiene registro de hoy
        today_log = DailyWorkLog.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        # Rendimiento de la semana
        week_perf = DailyWorkLog.objects.filter(
            employee=employee,
            date__gte=week_ago
        ).aggregate(
            avg_packages=Avg('packages_processed'),
            avg_quality=Avg('quality_score'),
        )
        
        employees_with_status.append({
            'employee': employee,
            'is_active_today': today_log is not None,
            'week_performance': week_perf,
        })
    
    # Estadísticas del equipo
    team_stats = {
        'total_employees': supervised_employees.count(),
        'active_today': DailyWorkLog.objects.filter(
            employee__supervisor=request.user,
            date=today
        ).count(),
    }
    
    # Tareas pendientes del equipo
    pending_tasks = Task.objects.filter(
        assigned_to__supervisor=request.user,
        status='pending'
    ).select_related('assigned_to__user')[:10]
    
    # Tareas vencidas
    overdue_tasks = Task.objects.filter(
        assigned_to__supervisor=request.user,
        status__in=['pending', 'in_progress'],
        due_date__lt=datetime.now()
    ).select_related('assigned_to__user')[:5]
    
    # Rendimiento del equipo - Semana actual (últimos 7 días)
    week_ago = today - timedelta(days=7)
    current_week_performance = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=week_ago,
        date__lte=today
    ).aggregate(
        avg_packages=Avg('packages_processed'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents'),
        total_packages=Sum('packages_processed'),
        total_trucks_received=Sum('trucks_received'),
        total_trucks_dispatched=Sum('trucks_dispatched'),
    )
    
    # Rendimiento del equipo - Semana pasada (7 días anteriores)
    two_weeks_ago = today - timedelta(days=14)
    previous_week_performance = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=two_weeks_ago,
        date__lt=week_ago
    ).aggregate(
        avg_packages=Avg('packages_processed'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents'),
        total_packages=Sum('packages_processed'),
        total_trucks_received=Sum('trucks_received'),
        total_trucks_dispatched=Sum('trucks_dispatched'),
    )
    
    # Calcular comparaciones
    def calculate_change(current, previous):
        if previous and previous > 0:
            return ((current or 0) - previous) / previous * 100
        elif current:
            return 100
        return 0
    
    packages_change = calculate_change(
        current_week_performance.get('avg_packages') or 0,
        previous_week_performance.get('avg_packages') or 0
    )
    quality_change = calculate_change(
        current_week_performance.get('avg_quality') or 0,
        previous_week_performance.get('avg_quality') or 0
    )
    incidents_change = calculate_change(
        current_week_performance.get('total_incidents') or 0,
        previous_week_performance.get('total_incidents') or 0
    )
    
    performance_comparison = {
        'packages_change': packages_change,
        'packages_change_abs': abs(packages_change),
        'quality_change': quality_change,
        'quality_change_abs': abs(quality_change),
        'incidents_change': incidents_change,
        'incidents_change_abs': abs(incidents_change),
    }
    
    # Datos para gráficos (últimos 30 días)
    thirty_days_ago = today - timedelta(days=30)
    daily_performance = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=thirty_days_ago
    ).values('date').annotate(
        total_packages=Sum('packages_processed'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents')
    ).order_by('date')
    
    # Preparar datos para Chart.js (serializar como JSON)
    chart_data_json = json.dumps({
        'dates': [str(d['date']) for d in daily_performance],
        'packages': [d['total_packages'] or 0 for d in daily_performance],
        'quality': [float(d['avg_quality'] or 0) for d in daily_performance],
        'incidents': [d['total_incidents'] or 0 for d in daily_performance],
    }, cls=DjangoJSONEncoder)
    
    # Estadísticas de tareas
    task_stats = {
        'total_pending': Task.objects.filter(
            assigned_to__supervisor=request.user,
            status='pending'
        ).count(),
        'total_in_progress': Task.objects.filter(
            assigned_to__supervisor=request.user,
            status='in_progress'
        ).count(),
        'total_completed_week': Task.objects.filter(
            assigned_to__supervisor=request.user,
            status='completed',
            completion_date__gte=week_ago
        ).count(),
        'total_overdue': overdue_tasks.count(),
    }
    
    context = {
        'user': request.user,
        'supervised_employees': supervised_employees,
        'employees_with_status': employees_with_status,
        'team_stats': team_stats,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'team_performance': current_week_performance,
        'previous_week_performance': previous_week_performance,
        'performance_comparison': performance_comparison,
        'chart_data_json': chart_data_json,
        'task_stats': task_stats,
    }
    
    return render(request, 'supervisor/dashboard.html', context)


@login_required
def employee_dashboard(request):
    """Dashboard para empleados"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        employee = None
    
    # Si el usuario tiene rol 'employee' pero no tiene perfil, crearlo automáticamente
    if not employee and request.user.role == 'employee':
        # Obtener o crear departamento por defecto
        department, _ = Department.objects.get_or_create(
            name='General',
            defaults={'description': 'Departamento por defecto'}
        )
        
        # Crear perfil de empleado
        try:
            employee = Employee.objects.create(
                user=request.user,
                employee_id=f"EMP{request.user.id:04d}",
                position=None,
                hire_date=date.today(),
                supervisor=None
            )
        except Exception as e:
            # Si falla la creación, intentar obtener de nuevo
            try:
                employee = request.user.employee_profile
            except Employee.DoesNotExist:
                employee = None
    
    # Si aún no hay perfil, mostrar error (solo para usuarios que no son empleados)
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
    
    # Rendimiento de la semana (últimos 7 días)
    week_ago = today - timedelta(days=6)  # 6 días atrás + hoy = 7 días totales
    week_performance = DailyWorkLog.objects.filter(
        employee=employee,
        date__gte=week_ago,
        date__lte=today
    ).aggregate(
        total_packages=Sum('packages_processed'),
        total_trucks=Sum('trucks_received') + Sum('trucks_dispatched'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents')
    )
    
    # Estadísticas de tareas del empleado
    all_my_tasks = Task.objects.filter(assigned_to=employee)
    week_performance['my_tasks_pending'] = all_my_tasks.filter(status='pending').count()
    week_performance['my_tasks_completed'] = all_my_tasks.filter(status='completed').count()
    
    # Historial de rendimiento (últimos 7 días, incluyendo hoy)
    performance_history = DailyWorkLog.objects.filter(
        employee=employee,
        date__gte=week_ago,
        date__lte=today
    ).order_by('date')
    
    # Preparar datos para el gráfico (últimos 7 días, desde hace 6 días hasta hoy)
    chart_data = {
        'labels': [],
        'packages': [],
        'quality': [],
        'trucks': []
    }
    
    # Generar todos los días desde hace 6 días hasta hoy (7 días totales)
    for i in range(7):
        day_date = week_ago + timedelta(days=i)
        chart_data['labels'].append(day_date.strftime('%d/%m'))
        
        # Buscar registro para este día
        day_log = next((log for log in performance_history if log.date == day_date), None)
        if day_log:
            chart_data['packages'].append(day_log.packages_processed or 0)
            chart_data['quality'].append(float(day_log.quality_score or 0))
            chart_data['trucks'].append((day_log.trucks_received or 0) + (day_log.trucks_dispatched or 0))
        else:
            chart_data['packages'].append(0)
            chart_data['quality'].append(0)
            chart_data['trucks'].append(0)
    
    context = {
        'user': request.user,
        'employee': employee,
        'today_log': today_log,
        'my_tasks': my_tasks,
        'week_performance': week_performance,
        'performance_history': performance_history,
        'chart_data': {
            'labels': mark_safe(json.dumps(chart_data['labels'])),
            'packages': mark_safe(json.dumps(chart_data['packages'])),
            'quality': mark_safe(json.dumps(chart_data['quality'])),
            'trucks': mark_safe(json.dumps(chart_data['trucks'])),
        },
    }
    
    return render(request, 'employee/dashboard.html', context)


def access_denied_view(request):
    """Vista para mostrar página de acceso restringido"""
    return render(request, 'auth/access_denied.html', {
        'user': request.user if request.user.is_authenticated else None
    })


@login_required
def supervisor_employees_list(request):
    """Lista de empleados supervisados"""
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position', 'position__department').order_by('user__first_name', 'user__last_name')
    
    # Estadísticas por empleado
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    employees_data = []
    for employee in supervised_employees:
        # Registro de hoy
        today_log = DailyWorkLog.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        # Rendimiento de la semana
        week_performance = DailyWorkLog.objects.filter(
            employee=employee,
            date__gte=week_ago
        ).aggregate(
            avg_packages=Avg('packages_processed'),
            avg_quality=Avg('quality_score'),
            total_incidents=Sum('safety_incidents')
        )
        
        employees_data.append({
            'employee': employee,
            'is_active_today': today_log is not None,
            'week_performance': week_performance,
        })
    
    context = {
        'user': request.user,
        'employees_data': employees_data,
    }
    
    return render(request, 'supervisor/employees_list.html', context)


@login_required
def supervisor_team_reports(request):
    """Reportes del equipo para supervisor"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Empleados supervisados
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position')
    
    # Reporte semanal
    weekly_report = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=week_ago
    ).aggregate(
        total_packages=Sum('packages_processed'),
        total_trucks_received=Sum('trucks_received'),
        total_trucks_dispatched=Sum('trucks_dispatched'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents'),
        total_work_logs=Count('id')
    )
    
    # Reporte mensual
    monthly_report = DailyWorkLog.objects.filter(
        employee__supervisor=request.user,
        date__gte=month_ago
    ).aggregate(
        total_packages=Sum('packages_processed'),
        total_trucks_received=Sum('trucks_received'),
        total_trucks_dispatched=Sum('trucks_dispatched'),
        avg_quality=Avg('quality_score'),
        total_incidents=Sum('safety_incidents'),
        total_work_logs=Count('id')
    )
    
    # Rendimiento por empleado (últimos 7 días)
    employee_performance = []
    for employee in supervised_employees:
        perf = DailyWorkLog.objects.filter(
            employee=employee,
            date__gte=week_ago
        ).aggregate(
            avg_packages=Avg('packages_processed'),
            avg_quality=Avg('quality_score'),
            total_incidents=Sum('safety_incidents'),
            days_worked=Count('id', distinct=True)
        )
        
        employee_performance.append({
            'employee': employee,
            'performance': perf,
        })
    
    # Ordenar por promedio de paquetes
    employee_performance.sort(key=lambda x: x['performance']['avg_packages'] or 0, reverse=True)
    
    context = {
        'user': request.user,
        'supervised_employees': supervised_employees,
        'weekly_report': weekly_report,
        'monthly_report': monthly_report,
        'employee_performance': employee_performance,
    }
    
    return render(request, 'supervisor/team_reports.html', context)


@login_required
def supervisor_evaluate_performance(request, employee_id=None):
    """Evaluar rendimiento de empleados"""
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position')
    
    employee = None
    if employee_id:
        try:
            employee = supervised_employees.get(id=employee_id)
        except Employee.DoesNotExist:
            pass
    
    # Si se seleccionó un empleado, mostrar su rendimiento detallado
    employee_performance_data = None
    if employee:
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Rendimiento de la semana
        week_perf = DailyWorkLog.objects.filter(
            employee=employee,
            date__gte=week_ago
        ).aggregate(
            avg_packages=Avg('packages_processed'),
            avg_quality=Avg('quality_score'),
            total_incidents=Sum('safety_incidents'),
            days_worked=Count('id')
        )
        
        # Rendimiento del mes
        month_perf = DailyWorkLog.objects.filter(
            employee=employee,
            date__gte=month_ago
        ).aggregate(
            avg_packages=Avg('packages_processed'),
            avg_quality=Avg('quality_score'),
            total_incidents=Sum('safety_incidents'),
            days_worked=Count('id')
        )
        
        # Últimos registros
        recent_logs = DailyWorkLog.objects.filter(
            employee=employee
        ).order_by('-date')[:10]
        
        employee_performance_data = {
            'week': week_perf,
            'month': month_perf,
            'recent_logs': recent_logs,
        }
    
    context = {
        'user': request.user,
        'supervised_employees': supervised_employees,
        'selected_employee': employee,
        'employee_performance': employee_performance_data,
    }
    
    return render(request, 'supervisor/evaluate_performance.html', context)


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