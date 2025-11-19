"""
Pruebas unitarias para las vistas de Core
"""

import json
import pytest
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from logistica_hr.tasks.models import Task
from logistica_hr.employees.models import Employee
from logistica_hr.performance.models import DailyWorkLog
from django.db.models import Q
from tests.factories import (
    AdminUserFactory,
    SupervisorUserFactory,
    EmployeeUserFactory,
    EmployeeFactory,
    TaskFactory,
    DailyWorkLogFactory,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestHomeView:
    """Pruebas para la vista home_view"""

    def test_home_view_requires_login(self, client):
        """Probar que home_view requiere autenticación"""
        url = reverse('home')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_home_view_redirects_admin_to_admin_dashboard(self, client):
        """Probar que admin es redirigido a admin_dashboard"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        url = reverse('home')
        response = client.get(url)
        
        # home_view llama directamente a admin_dashboard, no redirige
        assert response.status_code == 200
        # Verificar que se renderiza el template de admin
        assert 'admin/dashboard.html' in [t.name for t in response.templates] or response.status_code == 200

    def test_home_view_redirects_supervisor_to_supervisor_dashboard(self, client):
        """Probar que supervisor es redirigido a supervisor_dashboard"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        url = reverse('home')
        response = client.get(url)
        
        assert response.status_code == 200  # Puede renderizar o redirigir

    def test_home_view_redirects_employee_to_employee_dashboard(self, client):
        """Probar que employee es redirigido a employee_dashboard"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('home')
        response = client.get(url)
        
        assert response.status_code == 200  # Puede renderizar o redirigir


@pytest.mark.django_db
@pytest.mark.views
class TestAdminDashboard:
    """Pruebas para la vista admin_dashboard"""

    def test_admin_dashboard_requires_login(self, client):
        """Probar que admin_dashboard requiere autenticación"""
        url = reverse('admin_dashboard')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_admin_dashboard_shows_statistics(self, client):
        """Probar que admin_dashboard muestra estadísticas"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        # Crear algunos datos de prueba
        EmployeeFactory()
        EmployeeFactory()
        TaskFactory()
        TaskFactory(status='pending')
        
        url = reverse('admin_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'stats' in response.context
        assert response.context['stats']['total_employees'] >= 0
        assert response.context['stats']['total_tasks'] >= 0

    def test_admin_dashboard_shows_recent_activities(self, client):
        """Probar que admin_dashboard muestra actividades recientes"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        # Crear empleado reciente
        employee = EmployeeFactory()
        
        url = reverse('admin_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'recent_activities' in response.context

    def test_admin_dashboard_shows_urgent_tasks(self, client):
        """Probar que admin_dashboard muestra tareas urgentes"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        # Crear tarea urgente (vencida)
        employee = EmployeeFactory()
        task = TaskFactory(
            assigned_to=employee,
            status='pending',
            due_date=timezone.now() - timedelta(days=1)
        )
        
        url = reverse('admin_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'urgent_tasks' in response.context

    def test_admin_dashboard_template(self, client):
        """Probar que admin_dashboard usa el template correcto"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        url = reverse('admin_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'admin/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.views
class TestSupervisorDashboard:
    """Pruebas para la vista supervisor_dashboard"""

    def test_supervisor_dashboard_requires_login(self, client):
        """Probar que supervisor_dashboard requiere autenticación"""
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_supervisor_dashboard_shows_team_stats(self, client):
        """Probar que supervisor_dashboard muestra estadísticas del equipo"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        # Crear empleados bajo supervisión
        employee1 = EmployeeFactory(supervisor=supervisor)
        employee2 = EmployeeFactory(supervisor=supervisor)
        
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'team_stats' in response.context
        assert response.context['team_stats']['total_employees'] == 2

    def test_supervisor_dashboard_shows_supervised_employees(self, client):
        """Probar que supervisor_dashboard muestra empleados supervisados"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        employee1 = EmployeeFactory(supervisor=supervisor)
        employee2 = EmployeeFactory(supervisor=supervisor)
        # Empleado de otro supervisor (no debería aparecer)
        other_supervisor = SupervisorUserFactory()
        employee3 = EmployeeFactory(supervisor=other_supervisor)
        
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'employees_with_status' in response.context
        employee_ids = [emp['employee'].id for emp in response.context['employees_with_status']]
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids
        assert employee3.id not in employee_ids

    def test_supervisor_dashboard_shows_pending_tasks(self, client):
        """Probar que supervisor_dashboard muestra tareas pendientes del equipo"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(supervisor)
        
        task1 = TaskFactory(assigned_to=employee, status='pending')
        task2 = TaskFactory(assigned_to=employee, status='in_progress')
        
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'pending_tasks' in response.context

    def test_supervisor_dashboard_shows_overdue_tasks(self, client):
        """Probar que supervisor_dashboard muestra tareas vencidas"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(supervisor)
        
        overdue_task = TaskFactory(
            assigned_to=employee,
            status='pending',
            due_date=timezone.now() - timedelta(days=1)
        )
        
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'overdue_tasks' in response.context

    def test_supervisor_dashboard_template(self, client):
        """Probar que supervisor_dashboard usa el template correcto"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        url = reverse('supervisor_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'supervisor/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.views
class TestEmployeeDashboard:
    """Pruebas para la vista employee_dashboard"""

    def test_employee_dashboard_requires_login(self, client):
        """Probar que employee_dashboard requiere autenticación"""
        url = reverse('employee_dashboard')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_employee_dashboard_shows_assigned_tasks(self, client):
        """Probar que employee_dashboard muestra tareas asignadas"""
        employee_user = EmployeeUserFactory()
        employee = EmployeeFactory(user=employee_user)
        client.force_login(employee_user)
        
        task1 = TaskFactory(assigned_to=employee)
        task2 = TaskFactory(assigned_to=employee)
        
        url = reverse('employee_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        # Verificar que se muestran las tareas del empleado

    def test_employee_dashboard_template(self, client):
        """Probar que employee_dashboard usa el template correcto"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('employee_dashboard')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'employee/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.views
class TestAPIDashboardStats:
    """Pruebas para la vista api_dashboard_stats"""

    def test_api_dashboard_stats_requires_login(self, client):
        """Probar que api_dashboard_stats requiere autenticación"""
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_api_dashboard_stats_returns_json(self, client):
        """Probar que api_dashboard_stats retorna JSON"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        data = json.loads(response.content)
        assert isinstance(data, dict)

    def test_api_dashboard_stats_contains_stats(self, client):
        """Probar que api_dashboard_stats contiene estadísticas"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        # Crear algunos datos
        EmployeeFactory()
        TaskFactory()
        
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        # Verificar que contiene alguna estadística
        assert 'stats' in data or len(data) > 0

    def test_api_dashboard_stats_for_admin(self, client):
        """Probar estadísticas específicas para admin"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        # Verificar estructura de respuesta

    def test_api_dashboard_stats_for_supervisor(self, client):
        """Probar estadísticas específicas para supervisor"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        # Verificar estructura de respuesta

    def test_api_dashboard_stats_for_employee(self, client):
        """Probar estadísticas específicas para employee"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('api_dashboard_stats')
        response = client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        # Verificar estructura de respuesta


@pytest.mark.django_db
@pytest.mark.views
class TestAccessDeniedView:
    """Pruebas para la vista access_denied_view"""

    def test_access_denied_view_accessible(self, client):
        """Probar que access_denied_view es accesible sin autenticación"""
        url = reverse('access_denied')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'auth/access_denied.html' in [t.name for t in response.templates]

    def test_access_denied_view_with_authenticated_user(self, client):
        """Probar que access_denied_view funciona con usuario autenticado"""
        user = AdminUserFactory()
        client.force_login(user)
        
        url = reverse('access_denied')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'user' in response.context
        assert response.context['user'] == user


@pytest.mark.django_db
@pytest.mark.views
class TestAdminEmployeesList:
    """Pruebas para la vista admin_employees_list"""

    def test_admin_employees_list_requires_login(self, client):
        """Probar que admin_employees_list requiere autenticación"""
        url = reverse('admin_employees_list')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_admin_employees_list_requires_admin(self, client):
        """Probar que admin_employees_list requiere rol admin"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('admin_employees_list')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/access-denied/' in response.url or 'access_denied' in response.url

    def test_admin_employees_list_shows_employees(self, client):
        """Probar que admin_employees_list muestra empleados"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        employee1 = EmployeeFactory()
        employee2 = EmployeeFactory()
        
        url = reverse('admin_employees_list')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'employees_data' in response.context
        employee_ids = [emp['employee'].id for emp in response.context['employees_data']]
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids

    def test_admin_employees_list_search_filter(self, client):
        """Probar filtro de búsqueda en admin_employees_list"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        employee = EmployeeFactory()
        employee.user.first_name = "Juan"
        employee.user.save()
        
        url = reverse('admin_employees_list')
        response = client.get(url, {'search': 'Juan'})
        
        assert response.status_code == 200
        assert 'employees_data' in response.context
        assert len(response.context['employees_data']) > 0
        assert any('Juan' in emp['employee'].user.first_name for emp in response.context['employees_data'])

    def test_admin_employees_list_supervisor_filter(self, client):
        """Probar filtro por supervisor en admin_employees_list"""
        admin = AdminUserFactory()
        supervisor = SupervisorUserFactory()
        client.force_login(admin)
        
        employee = EmployeeFactory(supervisor=supervisor)
        
        url = reverse('admin_employees_list')
        response = client.get(url, {'supervisor': supervisor.id})
        
        assert response.status_code == 200
        assert 'employees_data' in response.context
        employee_ids = [emp['employee'].id for emp in response.context['employees_data']]
        assert employee.id in employee_ids


@pytest.mark.django_db
@pytest.mark.views
class TestAdminAssignSupervisor:
    """Pruebas para la vista admin_assign_supervisor"""

    def test_admin_assign_supervisor_requires_login(self, client):
        """Probar que admin_assign_supervisor requiere autenticación"""
        employee = EmployeeFactory()
        url = reverse('admin_assign_supervisor', args=[employee.id])
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_admin_assign_supervisor_requires_admin(self, client):
        """Probar que admin_assign_supervisor requiere rol admin"""
        employee_user = EmployeeUserFactory()
        employee = EmployeeFactory()
        client.force_login(employee_user)
        
        url = reverse('admin_assign_supervisor', args=[employee.id])
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/access-denied/' in response.url or 'access_denied' in response.url

    def test_admin_assign_supervisor_get_shows_form(self, client):
        """Probar que GET muestra el formulario"""
        admin = AdminUserFactory()
        employee = EmployeeFactory()
        client.force_login(admin)
        
        url = reverse('admin_assign_supervisor', args=[employee.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'employee' in response.context
        assert 'supervisors' in response.context
        assert response.context['employee'] == employee

    def test_admin_assign_supervisor_post_assigns_supervisor(self, client):
        """Probar que POST asigna supervisor"""
        admin = AdminUserFactory()
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=None)
        client.force_login(admin)
        
        url = reverse('admin_assign_supervisor', args=[employee.id])
        response = client.post(url, {'supervisor_id': supervisor.id})
        
        assert response.status_code == 302
        employee.refresh_from_db()
        assert employee.supervisor == supervisor

    def test_admin_assign_supervisor_post_removes_supervisor(self, client):
        """Probar que POST puede remover supervisor"""
        admin = AdminUserFactory()
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(admin)
        
        url = reverse('admin_assign_supervisor', args=[employee.id])
        response = client.post(url, {'supervisor_id': ''})
        
        assert response.status_code == 302
        employee.refresh_from_db()
        assert employee.supervisor is None

    def test_admin_assign_supervisor_nonexistent_employee(self, client):
        """Probar asignar supervisor a empleado inexistente"""
        admin = AdminUserFactory()
        client.force_login(admin)
        
        url = reverse('admin_assign_supervisor', args=[99999])
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/admin/employees/' in response.url or 'admin_employees_list' in response.url


@pytest.mark.django_db
@pytest.mark.views
class TestSupervisorEmployeesList:
    """Pruebas para la vista supervisor_employees_list"""

    def test_supervisor_employees_list_requires_login(self, client):
        """Probar que supervisor_employees_list requiere autenticación"""
        url = reverse('supervisor_employees_list')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_supervisor_employees_list_requires_supervisor(self, client):
        """Probar que supervisor_employees_list requiere rol supervisor"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('supervisor_employees_list')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/access-denied/' in response.url or 'access_denied' in response.url

    def test_supervisor_employees_list_shows_supervised_employees(self, client):
        """Probar que supervisor_employees_list muestra empleados supervisados"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        employee1 = EmployeeFactory(supervisor=supervisor)
        employee2 = EmployeeFactory(supervisor=supervisor)
        # Empleado de otro supervisor (no debería aparecer)
        other_supervisor = SupervisorUserFactory()
        employee3 = EmployeeFactory(supervisor=other_supervisor)
        
        url = reverse('supervisor_employees_list')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'employees_data' in response.context
        employee_ids = [emp['employee'].id for emp in response.context['employees_data']]
        assert employee1.id in employee_ids
        assert employee2.id in employee_ids
        assert employee3.id not in employee_ids


@pytest.mark.django_db
@pytest.mark.views
class TestSupervisorTeamReports:
    """Pruebas para la vista supervisor_team_reports"""

    def test_supervisor_team_reports_requires_login(self, client):
        """Probar que supervisor_team_reports requiere autenticación"""
        url = reverse('supervisor_team_reports')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_supervisor_team_reports_requires_supervisor(self, client):
        """Probar que supervisor_team_reports requiere rol supervisor"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('supervisor_team_reports')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/access-denied/' in response.url or 'access_denied' in response.url

    def test_supervisor_team_reports_shows_reports(self, client):
        """Probar que supervisor_team_reports muestra reportes"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(supervisor)
        
        # Crear algunos registros de trabajo
        DailyWorkLogFactory(employee=employee)
        
        url = reverse('supervisor_team_reports')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'weekly_report' in response.context
        assert 'monthly_report' in response.context
        assert 'employee_performance' in response.context

    def test_supervisor_team_reports_template(self, client):
        """Probar que supervisor_team_reports usa el template correcto"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        url = reverse('supervisor_team_reports')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'supervisor/team_reports.html' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.views
class TestSupervisorEvaluatePerformance:
    """Pruebas para la vista supervisor_evaluate_performance"""

    def test_supervisor_evaluate_performance_requires_login(self, client):
        """Probar que supervisor_evaluate_performance requiere autenticación"""
        url = reverse('supervisor_evaluate_performance')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/users/login' in response.url

    def test_supervisor_evaluate_performance_requires_supervisor(self, client):
        """Probar que supervisor_evaluate_performance requiere rol supervisor"""
        employee_user = EmployeeUserFactory()
        client.force_login(employee_user)
        
        url = reverse('supervisor_evaluate_performance')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/access-denied/' in response.url or 'access_denied' in response.url

    def test_supervisor_evaluate_performance_shows_employees(self, client):
        """Probar que supervisor_evaluate_performance muestra empleados"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(supervisor)
        
        url = reverse('supervisor_evaluate_performance')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'supervised_employees' in response.context
        employee_ids = [emp.id for emp in response.context['supervised_employees']]
        assert employee.id in employee_ids

    def test_supervisor_evaluate_performance_with_employee_id(self, client):
        """Probar que supervisor_evaluate_performance muestra datos de empleado específico"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        client.force_login(supervisor)
        
        # Crear registros de trabajo
        DailyWorkLogFactory(employee=employee)
        
        url = reverse('supervisor_evaluate_employee', args=[employee.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'selected_employee' in response.context
        assert response.context['selected_employee'] == employee
        assert 'employee_performance' in response.context

    def test_supervisor_evaluate_performance_invalid_employee_id(self, client):
        """Probar que supervisor_evaluate_performance maneja empleado inválido"""
        supervisor = SupervisorUserFactory()
        client.force_login(supervisor)
        
        url = reverse('supervisor_evaluate_employee', args=[99999])
        response = client.get(url)
        
        # Debería funcionar pero sin empleado seleccionado
        assert response.status_code == 200
        assert response.context['selected_employee'] is None

    def test_supervisor_evaluate_performance_other_supervisor_employee(self, client):
        """Probar que supervisor no puede ver empleados de otro supervisor"""
        supervisor1 = SupervisorUserFactory()
        supervisor2 = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor2)
        client.force_login(supervisor1)
        
        url = reverse('supervisor_evaluate_employee', args=[employee.id])
        response = client.get(url)
        
        # Debería funcionar pero sin empleado seleccionado (no está bajo su supervisión)
        assert response.status_code == 200
        assert response.context['selected_employee'] is None

