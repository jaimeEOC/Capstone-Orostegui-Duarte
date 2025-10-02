"""
Factories para crear datos de prueba usando Factory Boy
"""

import factory
from django.contrib.auth import get_user_model
from logistica_hr.employees.models import Department, Position, Employee
from logistica_hr.performance.models import PerformanceMetric, EmployeePerformance, DailyWorkLog
from logistica_hr.tasks.models import TaskCategory, Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory para crear usuarios de prueba"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = factory.Iterator(['admin', 'supervisor', 'employee'])
    phone = factory.Faker('phone_number')
    is_active = True
    is_verified = True


class AdminUserFactory(UserFactory):
    """Factory para crear usuarios administradores"""
    role = 'admin'
    username = factory.Sequence(lambda n: f'admin{n}')


class SupervisorUserFactory(UserFactory):
    """Factory para crear usuarios supervisores"""
    role = 'supervisor'
    username = factory.Sequence(lambda n: f'supervisor{n}')


class EmployeeUserFactory(UserFactory):
    """Factory para crear usuarios empleados"""
    role = 'employee'
    username = factory.Sequence(lambda n: f'employee{n}')


class DepartmentFactory(factory.django.DjangoModelFactory):
    """Factory para crear departamentos"""
    
    class Meta:
        model = Department
    
    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    manager = factory.SubFactory(SupervisorUserFactory)


class PositionFactory(factory.django.DjangoModelFactory):
    """Factory para crear posiciones"""
    
    class Meta:
        model = Position
    
    name = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=200)
    department = factory.SubFactory(DepartmentFactory)
    base_salary = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory para crear empleados"""
    
    class Meta:
        model = Employee
    
    user = factory.SubFactory(EmployeeUserFactory)
    employee_id = factory.Sequence(lambda n: f'EMP{n:04d}')
    position = factory.SubFactory(PositionFactory)
    hire_date = factory.Faker('date_this_year')
    supervisor = factory.SubFactory(SupervisorUserFactory)
    emergency_contact = factory.Faker('name')
    emergency_phone = factory.Faker('phone_number')
    skills = factory.List([
        factory.Faker('word') for _ in range(3)
    ])
    certifications = factory.List([
        factory.Faker('word') for _ in range(2)
    ])


class PerformanceMetricFactory(factory.django.DjangoModelFactory):
    """Factory para crear métricas de rendimiento"""
    
    class Meta:
        model = PerformanceMetric
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    metric_type = factory.Iterator(['productivity', 'quality', 'efficiency', 'attendance'])
    unit = factory.Faker('word')
    target_value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    weight = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, max_value=1.0)


class EmployeePerformanceFactory(factory.django.DjangoModelFactory):
    """Factory para crear rendimiento de empleados"""
    
    class Meta:
        model = EmployeePerformance
    
    employee = factory.SubFactory(EmployeeFactory)
    metric = factory.SubFactory(PerformanceMetricFactory)
    value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    date = factory.Faker('date_this_month')


class DailyWorkLogFactory(factory.django.DjangoModelFactory):
    """Factory para crear registros diarios de trabajo"""
    
    class Meta:
        model = DailyWorkLog
    
    employee = factory.SubFactory(EmployeeFactory)
    date = factory.Faker('date_this_month')
    hours_worked = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True, max_value=12.0)
    tasks_completed = factory.Faker('pyint', min_value=1, max_value=10)
    notes = factory.Faker('text', max_nb_chars=200)


class TaskCategoryFactory(factory.django.DjangoModelFactory):
    """Factory para crear categorías de tareas"""
    
    class Meta:
        model = TaskCategory
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    color = factory.Faker('hex_color')


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory para crear tareas"""
    
    class Meta:
        model = Task
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=300)
    category = factory.SubFactory(TaskCategoryFactory)
    assigned_to = factory.SubFactory(EmployeeFactory)
    priority = factory.Iterator(['low', 'medium', 'high', 'urgent'])
    status = factory.Iterator(['pending', 'in_progress', 'completed', 'cancelled'])
    due_date = factory.Faker('future_date', end_date='+30d')
