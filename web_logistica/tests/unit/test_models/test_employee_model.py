"""
Pruebas unitarias para los modelos de Employee
"""

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from logistica_hr.employees.models import Department, Position, Employee
from logistica_hr.users.models import User
from tests.factories import (
    DepartmentFactory, PositionFactory, EmployeeFactory,
    AdminUserFactory, SupervisorUserFactory, EmployeeUserFactory
)


@pytest.mark.django_db
@pytest.mark.models
class TestDepartmentModel:
    """Pruebas para el modelo Department"""

    def test_department_creation(self):
        """Probar creación básica de departamento"""
        dept = DepartmentFactory()
        assert dept.pk is not None
        assert dept.name is not None
        assert dept.is_active is True

    def test_department_str_representation(self):
        """Probar representación string del departamento"""
        dept = DepartmentFactory(name='Logística')
        assert str(dept) == 'Logística'

    def test_department_name_unique(self):
        """Probar que el nombre del departamento debe ser único"""
        name = 'Departamento Test'
        DepartmentFactory(name=name)
        
        with pytest.raises(IntegrityError):
            DepartmentFactory(name=name)

    def test_department_manager_optional(self):
        """Probar que el manager es opcional"""
        dept = DepartmentFactory(manager=None)
        assert dept.manager is None

    def test_department_manager_relationship(self):
        """Probar relación con el manager"""
        manager = SupervisorUserFactory()
        dept = DepartmentFactory(manager=manager)
        assert dept.manager == manager
        assert dept in manager.managed_departments.all()

    def test_department_ordering(self):
        """Probar ordenamiento por nombre"""
        dept1 = DepartmentFactory(name='Zulu')
        dept2 = DepartmentFactory(name='Alpha')
        dept3 = DepartmentFactory(name='Beta')
        
        departments = Department.objects.all()
        assert departments[0].name == 'Alpha'
        assert departments[1].name == 'Beta'
        assert departments[2].name == 'Zulu'


@pytest.mark.django_db
@pytest.mark.models
class TestPositionModel:
    """Pruebas para el modelo Position"""

    def test_position_creation(self):
        """Probar creación básica de posición"""
        position = PositionFactory()
        assert position.pk is not None
        assert position.name is not None
        assert position.department is not None

    def test_position_str_representation(self):
        """Probar representación string de la posición"""
        dept = DepartmentFactory(name='Logística')
        position = PositionFactory(name='Operador', department=dept)
        expected = 'Operador - Logística'
        assert str(position) == expected

    def test_position_department_required(self):
        """Probar que el departamento es requerido"""
        with pytest.raises(IntegrityError):
            PositionFactory(department=None)

    def test_position_base_salary_optional(self):
        """Probar que base_salary es opcional"""
        position = PositionFactory(base_salary=None)
        assert position.base_salary is None

    def test_position_base_salary_positive(self):
        """Probar que base_salary puede ser positivo"""
        position = PositionFactory(base_salary=50000.00)
        assert position.base_salary == 50000.00

    def test_position_ordering(self):
        """Probar ordenamiento por nombre"""
        pos1 = PositionFactory(name='Zulu Position')
        pos2 = PositionFactory(name='Alpha Position')
        pos3 = PositionFactory(name='Beta Position')
        
        positions = Position.objects.all().order_by('name')
        assert positions[0].name == 'Alpha Position'
        assert positions[1].name == 'Beta Position'
        assert positions[2].name == 'Zulu Position'


@pytest.mark.django_db
@pytest.mark.models
class TestEmployeeModel:
    """Pruebas para el modelo Employee"""

    def test_employee_creation(self):
        """Probar creación básica de empleado"""
        employee = EmployeeFactory()
        assert employee.pk is not None
        assert employee.user is not None
        assert employee.employee_id is not None

    def test_employee_str_representation(self):
        """Probar representación string del empleado"""
        user = EmployeeUserFactory(first_name='Juan', last_name='Pérez')
        employee = EmployeeFactory(user=user, employee_id='EMP001')
        expected = 'Juan Pérez (EMP001)'
        assert str(employee) == expected

    def test_employee_id_unique(self):
        """Probar que el employee_id debe ser único"""
        emp_id = 'EMP001'
        EmployeeFactory(employee_id=emp_id)
        
        with pytest.raises(IntegrityError):
            EmployeeFactory(employee_id=emp_id)

    def test_employee_user_one_to_one(self):
        """Probar relación one-to-one con User"""
        user = EmployeeUserFactory()
        employee1 = EmployeeFactory(user=user)
        
        with pytest.raises(IntegrityError):
            EmployeeFactory(user=user)

    def test_employee_position_optional(self):
        """Probar que la posición es opcional"""
        employee = EmployeeFactory(position=None)
        assert employee.position is None

    def test_employee_supervisor_optional(self):
        """Probar que el supervisor es opcional"""
        employee = EmployeeFactory(supervisor=None)
        assert employee.supervisor is None

    def test_employee_department_property(self):
        """Probar propiedad department"""
        dept = DepartmentFactory()
        position = PositionFactory(department=dept)
        employee = EmployeeFactory(position=position)
        assert employee.department == dept

    def test_employee_department_property_no_position(self):
        """Probar propiedad department cuando no hay posición"""
        employee = EmployeeFactory(position=None)
        assert employee.department is None

    def test_employee_years_of_service(self):
        """Probar cálculo de años de servicio"""
        hire_date = date.today() - timedelta(days=365 * 2 + 1)  # 2 años y 1 día atrás
        employee = EmployeeFactory(hire_date=hire_date)
        assert employee.years_of_service == 2

    def test_employee_years_of_service_less_than_year(self):
        """Probar años de servicio menor a un año"""
        hire_date = date.today() - timedelta(days=180)  # 6 meses atrás
        employee = EmployeeFactory(hire_date=hire_date)
        assert employee.years_of_service == 0

    def test_employee_skills_json_field(self):
        """Probar campo skills como JSON"""
        skills = ['Python', 'Django', 'Testing']
        employee = EmployeeFactory(skills=skills)
        assert employee.skills == skills

    def test_employee_certifications_json_field(self):
        """Probar campo certifications como JSON"""
        certifications = ['AWS Certified', 'Django Expert']
        employee = EmployeeFactory(certifications=certifications)
        assert employee.certifications == certifications

    def test_employee_emergency_contact_optional(self):
        """Probar que el contacto de emergencia es opcional"""
        employee = EmployeeFactory(emergency_contact='')
        assert employee.emergency_contact == ''

    def test_employee_emergency_phone_optional(self):
        """Probar que el teléfono de emergencia es opcional"""
        employee = EmployeeFactory(emergency_phone='')
        assert employee.emergency_phone == ''

    def test_employee_ordering(self):
        """Probar ordenamiento por employee_id"""
        emp1 = EmployeeFactory(employee_id='EMP003')
        emp2 = EmployeeFactory(employee_id='EMP001')
        emp3 = EmployeeFactory(employee_id='EMP002')
        
        employees = Employee.objects.all()
        assert employees[0].employee_id == 'EMP001'
        assert employees[1].employee_id == 'EMP002'
        assert employees[2].employee_id == 'EMP003'


@pytest.mark.django_db
@pytest.mark.models
class TestEmployeeModelValidation:
    """Pruebas de validación del modelo Employee"""

    def test_employee_id_max_length(self):
        """Probar longitud máxima del employee_id"""
        long_id = '1' * 21  # Más de 20 caracteres
        employee = EmployeeFactory(employee_id=long_id)
        
        with pytest.raises(ValidationError):
            employee.full_clean()

    def test_employee_emergency_contact_max_length(self):
        """Probar longitud máxima del emergency_contact"""
        long_contact = '1' * 101  # Más de 100 caracteres
        employee = EmployeeFactory(emergency_contact=long_contact)
        
        with pytest.raises(ValidationError):
            employee.full_clean()

    def test_employee_emergency_phone_max_length(self):
        """Probar longitud máxima del emergency_phone"""
        long_phone = '1' * 21  # Más de 20 caracteres
        employee = EmployeeFactory(emergency_phone=long_phone)
        
        with pytest.raises(ValidationError):
            employee.full_clean()


@pytest.mark.django_db
@pytest.mark.models
class TestEmployeeModelRelationships:
    """Pruebas de relaciones del modelo Employee"""

    def test_employee_supervisor_relationship(self):
        """Probar relación con supervisor"""
        supervisor = SupervisorUserFactory()
        employee = EmployeeFactory(supervisor=supervisor)
        assert employee.supervisor == supervisor
        assert employee in supervisor.supervised_employees.all()

    def test_employee_position_relationship(self):
        """Probar relación con posición"""
        position = PositionFactory()
        employee = EmployeeFactory(position=position)
        assert employee.position == position
        assert employee in position.employees.all()

    def test_employee_user_relationship(self):
        """Probar relación con usuario"""
        user = EmployeeUserFactory()
        employee = EmployeeFactory(user=user)
        assert employee.user == user
        assert hasattr(user, 'employee_profile')
        assert user.employee_profile == employee
