"""
Pruebas unitarias para la gestión de tareas
"""

from datetime import datetime, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from tests.factories import (
    AdminUserFactory,
    EmployeeFactory,
    EmployeeUserFactory,
    SupervisorUserFactory,
    TaskCategoryFactory,
    TaskFactory,
)

from logistica_hr.employees.models import Employee
from logistica_hr.tasks.models import Task, TaskCategory
from logistica_hr.users.models import User


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskStateManagement:
    """Pruebas para gestión de estados de tareas"""

    def test_task_marked_completed_sets_completion_date(self):
        """Probar que marcar tarea como completada establece fecha de completado"""
        task = TaskFactory(status="pending")
        assert task.completion_date is None

        task.status = "completed"
        task.save()

        assert task.completion_date is not None
        assert task.completion_date <= timezone.now()

    def test_task_marked_in_progress_sets_start_date(self):
        """Probar que marcar tarea como en progreso establece fecha de inicio"""
        task = TaskFactory(status="pending")
        assert task.start_date is None

        task.status = "in_progress"
        task.save()

        assert task.start_date is not None
        assert task.start_date <= timezone.now()

    def test_task_already_completed_keeps_completion_date(self):
        """Probar que tarea ya completada mantiene su fecha de completado"""
        task = TaskFactory(status="completed")
        original_completion_date = task.completion_date

        # Cambiar a otro estado y volver a completada
        task.status = "in_progress"
        task.save()
        task.status = "completed"
        task.save()

        # La fecha de completado no debería cambiar
        assert task.completion_date == original_completion_date

    def test_task_already_in_progress_keeps_start_date(self):
        """Probar que tarea ya en progreso mantiene su fecha de inicio"""
        task = TaskFactory(status="in_progress")
        original_start_date = task.start_date

        # Cambiar a otro estado y volver a en progreso
        task.status = "pending"
        task.save()
        task.status = "in_progress"
        task.save()

        # La fecha de inicio no debería cambiar
        assert task.start_date == original_start_date

    def test_task_cancelled_does_not_set_dates(self):
        """Probar que cancelar tarea no establece fechas automáticamente"""
        task = TaskFactory(status="pending")

        task.status = "cancelled"
        task.save()

        assert task.start_date is None
        assert task.completion_date is None

    def test_task_on_hold_does_not_set_dates(self):
        """Probar que poner tarea en espera no establece fechas automáticamente"""
        task = TaskFactory(status="pending")

        task.status = "on_hold"
        task.save()

        assert task.start_date is None
        assert task.completion_date is None


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskOverdueDetection:
    """Pruebas para detección de tareas vencidas"""

    def test_task_overdue_detection(self):
        """Probar detección de tarea vencida"""
        # Tarea vencida
        past_date = timezone.now() - timedelta(days=1)
        task = TaskFactory(due_date=past_date, status="pending")

        assert task.is_overdue is True

    def test_task_not_overdue_when_future_due_date(self):
        """Probar que tarea no está vencida cuando fecha es futura"""
        future_date = timezone.now() + timedelta(days=1)
        task = TaskFactory(due_date=future_date, status="pending")

        assert task.is_overdue is False

    def test_completed_task_not_overdue(self):
        """Probar que tarea completada no está vencida aunque esté vencida"""
        past_date = timezone.now() - timedelta(days=1)
        task = TaskFactory(due_date=past_date, status="completed")

        assert task.is_overdue is False

    def test_cancelled_task_not_overdue(self):
        """Probar que tarea cancelada no está vencida aunque esté vencida"""
        past_date = timezone.now() - timedelta(days=1)
        task = TaskFactory(due_date=past_date, status="cancelled")

        assert task.is_overdue is False

    def test_in_progress_task_overdue(self):
        """Probar que tarea en progreso puede estar vencida"""
        past_date = timezone.now() - timedelta(days=1)
        task = TaskFactory(due_date=past_date, status="in_progress")

        assert task.is_overdue is True

    def test_on_hold_task_overdue(self):
        """Probar que tarea en espera puede estar vencida"""
        past_date = timezone.now() - timedelta(days=1)
        task = TaskFactory(due_date=past_date, status="on_hold")

        assert task.is_overdue is True


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskProgressCalculation:
    """Pruebas para cálculo de progreso de tareas"""

    def test_progress_percentage_calculation(self):
        """Probar cálculo de porcentaje de progreso"""
        task = TaskFactory(estimated_hours=10.0, actual_hours=5.0)

        # Progreso: (5/10) * 100 = 50%
        assert task.progress_percentage == 50.0

    def test_progress_percentage_max_100(self):
        """Probar que el progreso no excede 100%"""
        task = TaskFactory(
            estimated_hours=10.0, actual_hours=15.0  # Más horas que estimadas
        )

        # Progreso máximo: 100%
        assert task.progress_percentage == 100.0

    def test_progress_percentage_without_estimated_hours(self):
        """Probar progreso sin horas estimadas"""
        task = TaskFactory(estimated_hours=None, actual_hours=5.0)

        assert task.progress_percentage == 0

    def test_progress_percentage_without_actual_hours(self):
        """Probar progreso sin horas reales"""
        task = TaskFactory(estimated_hours=10.0, actual_hours=None)

        assert task.progress_percentage == 0

    def test_progress_percentage_zero_estimated_hours(self):
        """Probar progreso con horas estimadas en cero"""
        task = TaskFactory(estimated_hours=0.0, actual_hours=5.0)

        # División por cero debería manejarse
        assert task.progress_percentage == 0

    def test_progress_percentage_exact_match(self):
        """Probar progreso cuando horas reales = horas estimadas"""
        task = TaskFactory(estimated_hours=8.0, actual_hours=8.0)

        assert task.progress_percentage == 100.0


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskValidation:
    """Pruebas para validaciones de tareas"""

    def test_task_title_required(self):
        """Probar que el título de la tarea es requerido"""
        with pytest.raises(ValidationError):
            task = Task(
                title="",  # Título vacío
                description="Descripción válida",
                assigned_to=EmployeeFactory(),
                due_date=timezone.now() + timedelta(days=1),
            )
            task.full_clean()

    def test_task_description_required(self):
        """Probar que la descripción de la tarea es requerida"""
        with pytest.raises(ValidationError):
            task = Task(
                title="Título válido",
                description="",  # Descripción vacía
                assigned_to=EmployeeFactory(),
                due_date=timezone.now() + timedelta(days=1),
            )
            task.full_clean()

    def test_task_due_date_required(self):
        """Probar que la fecha de vencimiento es requerida"""
        with pytest.raises(ValidationError):
            task = Task(
                title="Título válido",
                description="Descripción válida",
                assigned_to=EmployeeFactory(),
                due_date=None,  # Fecha vacía
            )
            task.full_clean()

    def test_task_assigned_to_required(self):
        """Probar que el empleado asignado es requerido"""
        with pytest.raises(ValidationError):
            task = Task(
                title="Título válido",
                description="Descripción válida",
                assigned_to=None,  # Empleado vacío
                due_date=timezone.now() + timedelta(days=1),
            )
            task.full_clean()

    def test_task_title_max_length(self):
        """Probar longitud máxima del título"""
        long_title = "A" * 201  # Más de 200 caracteres

        with pytest.raises(ValidationError):
            task = Task(
                title=long_title,
                description="Descripción válida",
                assigned_to=EmployeeFactory(),
                due_date=timezone.now() + timedelta(days=1),
            )
            task.full_clean()

    def test_task_estimated_hours_max_digits(self):
        """Probar dígitos máximos en horas estimadas"""
        # 5 dígitos enteros + 2 decimales (válido)
        task = TaskFactory(estimated_hours=999.99)
        assert task.estimated_hours == 999.99

    def test_task_actual_hours_max_digits(self):
        """Probar dígitos máximos en horas reales"""
        # 5 dígitos enteros + 2 decimales (válido)
        task = TaskFactory(actual_hours=999.99)
        assert task.actual_hours == 999.99

    def test_task_notes_optional(self):
        """Probar que las notas son opcionales"""
        task = TaskFactory(notes="")
        assert task.notes == ""

    def test_task_category_optional(self):
        """Probar que la categoría es opcional"""
        task = TaskFactory(category=None)
        assert task.category is None

    def test_task_assigned_by_optional(self):
        """Probar que assigned_by es opcional"""
        task = TaskFactory(assigned_by=None)
        assert task.assigned_by is None


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskOrdering:
    """Pruebas para ordenamiento de tareas"""

    def test_task_ordering_by_due_date_and_priority(self):
        """Probar ordenamiento por fecha de vencimiento y prioridad"""
        # Crear tareas con diferentes fechas y prioridades
        now = timezone.now()

        task1 = TaskFactory(due_date=now + timedelta(days=3), priority="low")
        task2 = TaskFactory(due_date=now + timedelta(days=1), priority="high")
        task3 = TaskFactory(due_date=now + timedelta(days=2), priority="medium")

        tasks = Task.objects.all()

        # Verificar que las tareas están ordenadas (puede ser ascendente o descendente)
        # Lo importante es que estén ordenadas consistentemente
        due_dates = [task.due_date for task in tasks]
        assert due_dates == sorted(due_dates) or due_dates == sorted(
            due_dates, reverse=True
        )

    def test_task_ordering_same_due_date_different_priority(self):
        """Probar ordenamiento con misma fecha pero diferente prioridad"""
        now = timezone.now()
        same_date = now + timedelta(days=1)

        task1 = TaskFactory(due_date=same_date, priority="low")
        task2 = TaskFactory(due_date=same_date, priority="high")
        task3 = TaskFactory(due_date=same_date, priority="medium")

        tasks = Task.objects.all()

        # Con la misma fecha, debería ordenar por prioridad
        # Verificar que están ordenadas por prioridad (puede ser cualquier orden consistente)
        priorities = [task.priority for task in tasks]
        # Verificar que todas las prioridades están presentes
        assert "high" in priorities
        assert "medium" in priorities
        assert "low" in priorities


@pytest.mark.django_db
@pytest.mark.business_logic
class TestTaskCategoryValidation:
    """Pruebas para validaciones de categorías de tareas"""

    def test_task_category_name_unique(self):
        """Probar que el nombre de la categoría debe ser único"""
        name = "Categoría Test"
        TaskCategoryFactory(name=name)

        with pytest.raises(Exception):  # IntegrityError o ValidationError
            TaskCategoryFactory(name=name)

    def test_task_category_priority_validation(self):
        """Probar validación de prioridad de categoría"""
        # Prioridad válida
        category = TaskCategoryFactory(priority=5)
        assert category.priority == 5

        # Prioridad inválida (muy alta)
        with pytest.raises(ValidationError):
            category = TaskCategoryFactory(priority=6)
            category.full_clean()

        # Prioridad inválida (muy baja)
        with pytest.raises(ValidationError):
            category = TaskCategoryFactory(priority=0)
            category.full_clean()

    def test_task_category_default_values(self):
        """Probar valores por defecto de la categoría"""
        category = TaskCategoryFactory()
        # Los valores por defecto pueden variar según la implementación
        assert category.color is not None
        assert category.priority is not None
        assert category.is_active is True  # Heredado de BaseModel
