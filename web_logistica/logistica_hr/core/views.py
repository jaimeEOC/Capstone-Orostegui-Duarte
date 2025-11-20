"""
Vistas principales del sistema Logistica HR
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Q
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, timedelta, date

from logistica_hr.users.models import User
from logistica_hr.users.forms import UserEditForm
from logistica_hr.employees.models import Employee
from logistica_hr.employees.forms import EmployeeEditForm
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
    total_supervisors = User.objects.filter(role='supervisor').count()
    
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
    
    # Estadísticas de la semana
    week_ago = today - timedelta(days=7)
    week_logs = DailyWorkLog.objects.filter(date__gte=week_ago)
    total_packages_week = week_logs.aggregate(total=Sum('packages_processed'))['total'] or 0
    avg_quality_week = week_logs.aggregate(avg=Avg('quality_score'))['avg'] or 0
    
    # Tareas
    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    overdue_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=datetime.now()
    ).count()
    
    # Actividades recientes reales
    recent_activities = []
    
    # Empleados recientemente creados (últimos 7 días)
    recent_employees = Employee.objects.filter(
        created_at__gte=week_ago
    ).select_related('user').order_by('-created_at')[:5]
    for emp in recent_employees:
        time_diff = datetime.now() - emp.created_at.replace(tzinfo=None)
        hours_ago = int(time_diff.total_seconds() / 3600)
        if hours_ago < 1:
            time_str = 'Hace menos de 1 hora'
            sort_key = 0
        elif hours_ago < 24:
            time_str = f'Hace {hours_ago} horas'
            sort_key = hours_ago
        else:
            days_ago = hours_ago // 24
            time_str = f'Hace {days_ago} días'
            sort_key = days_ago * 24
        
        # Convertir a timezone-naive para evitar problemas de comparación
        timestamp = emp.created_at
        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)
        
        recent_activities.append({
            'action': 'Nuevo empleado registrado',
            'user': emp.user.full_name,
            'time': time_str,
            'icon': 'user-plus',
            'color': '#4caf50',
            'sort_key': sort_key,
            'timestamp': timestamp
        })
    
    # Tareas completadas recientemente (últimos 7 días)
    recent_completed_tasks = Task.objects.filter(
        status='completed',
        updated_at__gte=week_ago
    ).select_related('assigned_to__user', 'assigned_by').order_by('-updated_at')[:5]
    for task in recent_completed_tasks:
        time_diff = datetime.now() - task.updated_at.replace(tzinfo=None)
        hours_ago = int(time_diff.total_seconds() / 3600)
        if hours_ago < 1:
            time_str = 'Hace menos de 1 hora'
            sort_key = 0
        elif hours_ago < 24:
            time_str = f'Hace {hours_ago} horas'
            sort_key = hours_ago
        else:
            days_ago = hours_ago // 24
            time_str = f'Hace {days_ago} días'
            sort_key = days_ago * 24
        
        # Convertir a timezone-naive para evitar problemas de comparación
        timestamp = task.updated_at
        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)
        
        recent_activities.append({
            'action': f'Tarea completada: {task.title[:30]}',
            'user': task.assigned_to.user.full_name if task.assigned_to else 'Desconocido',
            'time': time_str,
            'icon': 'check-circle',
            'color': '#2196f3',
            'sort_key': sort_key,
            'timestamp': timestamp
        })
    
    # Registros de trabajo de hoy
    today_work_logs = DailyWorkLog.objects.filter(date=today).select_related('employee__user')[:3]
    for log in today_work_logs:
        recent_activities.append({
            'action': f'Registro de trabajo: {log.packages_processed} paquetes procesados',
            'user': log.employee.user.full_name,
            'time': 'Hoy',
            'icon': 'clipboard-check',
            'color': '#ff9800',
            'sort_key': -1,  # Hoy es más reciente
            'timestamp': datetime.combine(today, datetime.min.time())
        })
    
    # Ordenar por timestamp (más recientes primero)
    # Asegurar que todos los timestamps sean timezone-naive
    for activity in recent_activities:
        if 'timestamp' in activity and activity['timestamp'] is not None:
            if hasattr(activity['timestamp'], 'tzinfo') and activity['timestamp'].tzinfo is not None:
                activity['timestamp'] = activity['timestamp'].replace(tzinfo=None)
    
    recent_activities.sort(key=lambda x: x.get('timestamp') or datetime.min, reverse=True)
    recent_activities = recent_activities[:10]  # Limitar a 10 actividades
    
    # Tareas pendientes y vencidas
    urgent_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=datetime.now() + timedelta(days=1)
    ).select_related('assigned_to__user', 'assigned_by').order_by('due_date')[:5]
    
    # Empleados recientes
    new_employees = Employee.objects.select_related('user', 'supervisor').order_by('-created_at')[:5]
    
    # Supervisores y sus equipos
    supervisors_with_teams = []
    supervisors = User.objects.filter(role='supervisor').select_related()
    for supervisor in supervisors:
        team_count = Employee.objects.filter(supervisor=supervisor).count()
        supervisors_with_teams.append({
            'supervisor': supervisor,
            'team_count': team_count
        })
    
    context = {
        'user': request.user,
        'stats': {
            'total_users': total_users,
            'total_employees': total_employees,
            'total_supervisors': total_supervisors,
            'total_packages_today': total_packages_today,
            'total_packages_week': total_packages_week,
            'total_trucks_today': total_trucks_today,
            'active_employees_today': active_employees_today,
            'avg_quality_week': round(avg_quality_week, 2) if avg_quality_week else 0,
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
        },
        'recent_activities': recent_activities,
        'urgent_tasks': urgent_tasks,
        'new_employees': new_employees,
        'supervisors_with_teams': supervisors_with_teams,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def supervisor_dashboard(request):
    """Dashboard para supervisores"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    thirty_days_ago = today - timedelta(days=30)
    
    # Empleados bajo supervisión con información de estado
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position')
    
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


@login_required
def admin_employees_list(request):
    """Lista de todos los empleados para administradores"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    # Obtener todos los empleados con información relacionada
    all_employees = Employee.objects.select_related(
        'user', 'position', 'supervisor'
    ).order_by('user__first_name', 'user__last_name')
    
    # Filtros
    search_query = request.GET.get('search', '')
    supervisor_filter = request.GET.get('supervisor', '')
    
    if search_query:
        all_employees = all_employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    if supervisor_filter:
        all_employees = all_employees.filter(supervisor_id=supervisor_filter)
    
    # Estadísticas por empleado
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    employees_data = []
    for employee in all_employees:
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
    
    # Obtener supervisores para filtros y mostrar en la lista
    supervisors = User.objects.filter(role='supervisor').order_by('first_name', 'last_name')
    
    # Preparar datos de supervisores para mostrar
    supervisors_data = []
    for supervisor in supervisors:
        employees_count = Employee.objects.filter(supervisor=supervisor).count()
        supervisors_data.append({
            'supervisor': supervisor,
            'employees_count': employees_count,
        })
    
    context = {
        'user': request.user,
        'employees_data': employees_data,
        'supervisors': supervisors,
        'supervisors_data': supervisors_data,
        'search_query': search_query,
        'supervisor_filter': supervisor_filter,
    }
    
    return render(request, 'admin/employees_list.html', context)


@login_required
def admin_assign_supervisor(request, employee_id):
    """Asignar supervisor a un empleado"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('admin_employees_list')
    
    if request.method == 'POST':
        supervisor_id = request.POST.get('supervisor_id')
        if supervisor_id:
            try:
                supervisor = User.objects.get(id=supervisor_id, role='supervisor')
                employee.supervisor = supervisor
                employee.save()
                # Refrescar desde la base de datos para asegurar que se guardó correctamente
                employee.refresh_from_db()
                messages.success(request, f'Supervisor asignado correctamente a {employee.user.full_name}.')
            except User.DoesNotExist:
                messages.error(request, 'Supervisor no encontrado.')
        else:
            # Remover supervisor
            employee.supervisor = None
            employee.save()
            # Refrescar desde la base de datos
            employee.refresh_from_db()
            messages.success(request, f'Supervisor removido de {employee.user.full_name}.')
        
        return redirect('admin_employees_list')
    
    # Obtener supervisores disponibles
    supervisors = User.objects.filter(role='supervisor').order_by('first_name', 'last_name')
    
    context = {
        'user': request.user,
        'employee': employee,
        'supervisors': supervisors,
    }
    
    return render(request, 'admin/assign_supervisor.html', context)


@login_required
def admin_edit_employee(request, employee_id):
    """Editar un empleado"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    try:
        employee = Employee.objects.select_related('user').get(id=employee_id)
    except Employee.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('admin_employees_list')
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=employee.user)
        employee_form = EmployeeEditForm(request.POST, instance=employee)
        
        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            messages.success(request, f'Empleado {employee.user.full_name} actualizado correctamente.')
            return redirect('admin_employees_list')
    else:
        user_form = UserEditForm(instance=employee.user)
        employee_form = EmployeeEditForm(instance=employee)
    
    context = {
        'user': request.user,
        'employee': employee,
        'user_form': user_form,
        'employee_form': employee_form,
    }
    
    return render(request, 'admin/edit_employee.html', context)


@login_required
def admin_delete_employee(request, employee_id):
    """Eliminar un empleado"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    try:
        employee = Employee.objects.select_related('user').get(id=employee_id)
    except Employee.DoesNotExist:
        messages.error(request, 'Empleado no encontrado.')
        return redirect('admin_employees_list')
    
    # Prevenir eliminación del propio usuario
    if employee.user == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('admin_employees_list')
    
    employee_name = employee.user.full_name
    
    if request.method == 'POST':
        # Eliminar el usuario (esto eliminará el empleado por CASCADE)
        employee.user.delete()
        messages.success(request, f'Empleado {employee_name} eliminado correctamente.')
        return redirect('admin_employees_list')
    
    context = {
        'user': request.user,
        'employee': employee,
    }
    
    return render(request, 'admin/delete_employee.html', context)


@login_required
def admin_edit_supervisor(request, supervisor_id):
    """Editar un supervisor"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    try:
        supervisor = User.objects.get(id=supervisor_id, role='supervisor')
    except User.DoesNotExist:
        messages.error(request, 'Supervisor no encontrado.')
        return redirect('admin_employees_list')
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=supervisor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supervisor {supervisor.full_name} actualizado correctamente.')
            return redirect('admin_employees_list')
    else:
        form = UserEditForm(instance=supervisor)
    
    context = {
        'user': request.user,
        'supervisor': supervisor,
        'form': form,
    }
    
    return render(request, 'admin/edit_supervisor.html', context)


@login_required
def admin_delete_supervisor(request, supervisor_id):
    """Eliminar un supervisor"""
    if not request.user.is_admin():
        return redirect('access_denied')
    
    try:
        supervisor = User.objects.get(id=supervisor_id, role='supervisor')
    except User.DoesNotExist:
        messages.error(request, 'Supervisor no encontrado.')
        return redirect('admin_employees_list')
    
    # Prevenir eliminación del propio usuario
    if supervisor == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('admin_employees_list')
    
    # Verificar si tiene empleados asignados
    employees_count = Employee.objects.filter(supervisor=supervisor).count()
    supervisor_name = supervisor.full_name
    
    if request.method == 'POST':
        # Si tiene empleados, remover la asignación primero
        if employees_count > 0:
            Employee.objects.filter(supervisor=supervisor).update(supervisor=None)
            messages.info(request, f'Se removieron {employees_count} empleado(s) del supervisor antes de eliminarlo.')
        
        supervisor.delete()
        messages.success(request, f'Supervisor {supervisor_name} eliminado correctamente.')
        return redirect('admin_employees_list')
    
    context = {
        'user': request.user,
        'supervisor': supervisor,
        'employees_count': employees_count,
    }
    
    return render(request, 'admin/delete_supervisor.html', context)


def access_denied_view(request):
    """Vista para mostrar página de acceso restringido"""
    return render(request, 'auth/access_denied.html', {
        'user': request.user if request.user.is_authenticated else None
    })


@login_required
def supervisor_employees_list(request):
    """Lista de empleados supervisados"""
    if not request.user.is_supervisor():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('access_denied')
    
    supervised_employees = Employee.objects.filter(
        supervisor=request.user
    ).select_related('user', 'position').order_by('user__first_name', 'user__last_name')
    
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
    if not request.user.is_supervisor():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('access_denied')
    
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
    if not request.user.is_supervisor():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('access_denied')
    
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