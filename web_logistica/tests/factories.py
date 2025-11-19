"""
Factories para crear datos de prueba usando Factory Boy
"""

from datetime import timedelta

import factory
from django.contrib.auth import get_user_model

from logistica_hr.employees.models import Department, Employee, Position
from logistica_hr.performance.models import (
    DailyWorkLog,
    EmployeePerformance,
    PerformanceEvaluation,
    PerformanceMetric,
)
from logistica_hr.tasks.models import Task, TaskCategory, TaskTimeLog, TaskComment

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory para crear usuarios de prueba"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = factory.Iterator(["admin", "supervisor", "employee"])
    phone = factory.Faker("phone_number")
    is_active = True
    is_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or "MySecurePass123!"
        self.set_password(password)
        self.save()


class AdminUserFactory(UserFactory):
    """Factory para crear usuarios administradores"""

    role = "admin"
    username = factory.Sequence(lambda n: f"admin{n}")


class SupervisorUserFactory(UserFactory):
    """Factory para crear usuarios supervisores"""

    role = "supervisor"
    username = factory.Sequence(lambda n: f"supervisor{n}")


class EmployeeUserFactory(UserFactory):
    """Factory para crear usuarios empleados"""

    role = "employee"
    username = factory.Sequence(lambda n: f"employee{n}")


class DepartmentFactory(factory.django.DjangoModelFactory):
    """Factory para crear departamentos"""

    class Meta:
        model = Department

    name = factory.Faker("company")
    description = factory.Faker("text", max_nb_chars=200)
    manager = factory.SubFactory(SupervisorUserFactory)


class PositionFactory(factory.django.DjangoModelFactory):
    """Factory para crear posiciones"""

    class Meta:
        model = Position

    name = factory.Faker("job")
    description = factory.Faker("text", max_nb_chars=200)
    department = factory.SubFactory(DepartmentFactory)
    base_salary = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory para crear empleados"""

    class Meta:
        model = Employee

    user = factory.SubFactory(EmployeeUserFactory)
    employee_id = factory.Sequence(lambda n: f"EMP{n:04d}")
    position = factory.SubFactory(PositionFactory)
    hire_date = factory.Faker("date_this_year")
    supervisor = factory.SubFactory(SupervisorUserFactory)
    emergency_contact = factory.Faker("name")
    emergency_phone = factory.Faker("phone_number")
    skills = factory.List([factory.Faker("word") for _ in range(3)])
    certifications = factory.List([factory.Faker("word") for _ in range(2)])


class PerformanceMetricFactory(factory.django.DjangoModelFactory):
    """Factory para crear métricas de rendimiento"""

    class Meta:
        model = PerformanceMetric

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=100)
    metric_type = factory.Iterator(
        ["productivity", "quality", "efficiency", "attendance"]
    )
    unit = factory.Faker("word")
    target_value = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, positive=True
    )
    weight = factory.Faker(
        "pydecimal", left_digits=2, right_digits=2, positive=True, max_value=1.0
    )


class EmployeePerformanceFactory(factory.django.DjangoModelFactory):
    """Factory para crear rendimiento de empleados"""

    class Meta:
        model = EmployeePerformance

    employee = factory.SubFactory(EmployeeFactory)
    metric = factory.SubFactory(PerformanceMetricFactory)
    actual_value = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, positive=True
    )
    date = factory.Faker("date_this_month")


class DailyWorkLogFactory(factory.django.DjangoModelFactory):
    """Factory para crear registros diarios de trabajo"""

    class Meta:
        model = DailyWorkLog

    employee = factory.SubFactory(EmployeeFactory)
    date = factory.Faker("date_this_month")
    start_time = factory.Faker("time")
    end_time = factory.Faker("time")
    total_break_time = factory.Faker("time_delta", end_datetime=None)
    packages_processed = factory.Faker("pyint", min_value=0, max_value=50)
    trucks_received = factory.Faker("pyint", min_value=0, max_value=20)
    trucks_dispatched = factory.Faker("pyint", min_value=0, max_value=20)
    quality_score = factory.Faker(
        "pydecimal", left_digits=1, right_digits=2, positive=True, max_value=7.0
    )
    safety_incidents = factory.Faker("pyint", min_value=0, max_value=5)
    notes = factory.Faker("text", max_nb_chars=200)


class PerformanceEvaluationFactory(factory.django.DjangoModelFactory):
    """Factory para crear evaluaciones de rendimiento"""

    class Meta:
        model = PerformanceEvaluation

    employee = factory.SubFactory(EmployeeFactory)
    evaluation_type = factory.Iterator(
        ["daily", "weekly", "monthly", "quarterly", "annual"]
    )
    start_date = factory.Faker("date_this_year")
    end_date = factory.Faker("date_this_year")
    overall_score = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, positive=True, max_value=100.0
    )
    evaluated_by = factory.SubFactory(SupervisorUserFactory)
    strengths = factory.Faker("text", max_nb_chars=200)
    areas_for_improvement = factory.Faker("text", max_nb_chars=200)
    recommendations = factory.Faker("text", max_nb_chars=200)


class TaskCategoryFactory(factory.django.DjangoModelFactory):
    """Factory para crear categorías de tareas"""

    class Meta:
        model = TaskCategory

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=100)
    color = factory.Faker("hex_color")


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory para crear tareas"""

    class Meta:
        model = Task

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=300)
    category = factory.SubFactory(TaskCategoryFactory)
    assigned_to = factory.SubFactory(EmployeeFactory)
    priority = factory.Iterator(["low", "medium", "high", "urgent"])
    status = factory.Iterator(["pending", "in_progress", "completed", "cancelled"])
    due_date = factory.Faker("future_date", end_date="+30d")


class TaskTimeLogFactory(factory.django.DjangoModelFactory):
    """Factory para crear registros de tiempo de tareas"""

    class Meta:
        model = TaskTimeLog

    task = factory.SubFactory(TaskFactory)
    employee = factory.SubFactory(EmployeeFactory)
    start_time = factory.Faker("date_time_this_year")
    end_time = factory.LazyAttribute(
        lambda obj: obj.start_time + timedelta(hours=2) if obj.start_time else None
    )
    description = factory.Faker("text", max_nb_chars=200)
    is_break = False


class TaskCommentFactory(factory.django.DjangoModelFactory):
    """Factory para crear comentarios de tareas"""

    class Meta:
        model = TaskComment

    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(EmployeeUserFactory)
    content = factory.Faker("text", max_nb_chars=500)
    is_internal = False
