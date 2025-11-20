"""
Pruebas unitarias para los modelos de Tasks
"""

import pytest
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from logistica_hr.tasks.models import Task, TaskCategory, TaskTimeLog, TaskComment
from tests.factories import (
    TaskFactory,
    TaskCategoryFactory,
    TaskTimeLogFactory,
    TaskCommentFactory,
    EmployeeFactory,
    EmployeeUserFactory,
    AdminUserFactory,
)


@pytest.mark.django_db
@pytest.mark.models
class TestTaskTimeLog:
    """Pruebas para el modelo TaskTimeLog"""

    def test_time_log_creation(self):
        """Probar creación básica de registro de tiempo"""
        time_log = TaskTimeLogFactory()
        assert time_log.pk is not None
        assert time_log.task is not None
        assert time_log.employee is not None
        assert time_log.start_time is not None

    def test_time_log_str_representation(self):
        """Probar representación string del registro"""
        task = TaskFactory(title="Tarea Importante")
        employee = EmployeeFactory()
        start = timezone.now()
        time_log = TaskTimeLogFactory(
            task=task, employee=employee, start_time=start
        )
        expected = f"Tarea Importante - {employee} - {start.date()}"
        assert str(time_log) == expected

    def test_time_log_end_time_optional(self):
        """Probar que end_time es opcional"""
        time_log = TaskTimeLogFactory(end_time=None)
        assert time_log.end_time is None

    def test_time_log_description_optional(self):
        """Probar que description es opcional"""
        time_log = TaskTimeLogFactory(description="")
        assert time_log.description == ""

    def test_time_log_is_break_default(self):
        """Probar valor por defecto de is_break"""
        time_log = TaskTimeLogFactory()
        assert time_log.is_break is False

    def test_time_log_is_break_true(self):
        """Probar que is_break puede ser True"""
        time_log = TaskTimeLogFactory(is_break=True)
        assert time_log.is_break is True

    def test_time_log_ordering(self):
        """Probar ordenamiento por start_time descendente"""
        now = timezone.now()
        log1 = TaskTimeLogFactory(start_time=now - timedelta(hours=2))
        log2 = TaskTimeLogFactory(start_time=now - timedelta(hours=1))
        log3 = TaskTimeLogFactory(start_time=now)

        logs = TaskTimeLog.objects.all()
        # Deberían estar ordenados por start_time descendente
        assert logs[0].start_time >= logs[1].start_time
        assert logs[1].start_time >= logs[2].start_time


@pytest.mark.django_db
@pytest.mark.models
class TestTaskTimeLogValidations:
    """Pruebas de validaciones de TaskTimeLog"""

    def test_time_log_end_time_after_start_time(self):
        """Probar que end_time debe ser posterior a start_time"""
        start = timezone.now()
        end = start + timedelta(hours=2)

        time_log = TaskTimeLogFactory(start_time=start, end_time=end)
        assert time_log.end_time > time_log.start_time

    def test_time_log_end_time_before_start_time_raises_error(self):
        """Probar que end_time antes de start_time lanza ValueError"""
        start = timezone.now()
        end = start - timedelta(hours=1)

        with pytest.raises(ValueError, match="La hora de fin debe ser posterior"):
            TaskTimeLogFactory(start_time=start, end_time=end)

    def test_time_log_end_time_equal_start_time_raises_error(self):
        """Probar que end_time igual a start_time lanza ValueError"""
        start = timezone.now()

        with pytest.raises(ValueError, match="La hora de fin debe ser posterior"):
            TaskTimeLogFactory(start_time=start, end_time=start)


@pytest.mark.django_db
@pytest.mark.models
class TestTaskTimeLogCalculations:
    """Pruebas para cálculos de TaskTimeLog"""

    def test_duration_hours_with_end_time(self):
        """Probar cálculo de duración en horas con end_time"""
        start = timezone.now()
        end = start + timedelta(hours=3, minutes=30)

        time_log = TaskTimeLogFactory(start_time=start, end_time=end)
        # 3.5 horas = 3 horas y 30 minutos
        assert abs(time_log.duration_hours - 3.5) < 0.01

    def test_duration_hours_exact_hours(self):
        """Probar cálculo de duración exacta en horas"""
        start = timezone.now()
        end = start + timedelta(hours=5)

        time_log = TaskTimeLogFactory(start_time=start, end_time=end)
        assert time_log.duration_hours == 5.0

    def test_duration_hours_with_minutes(self):
        """Probar cálculo de duración con minutos"""
        start = timezone.now()
        end = start + timedelta(hours=2, minutes=15)

        time_log = TaskTimeLogFactory(start_time=start, end_time=end)
        # 2.25 horas
        assert abs(time_log.duration_hours - 2.25) < 0.01

    def test_duration_hours_without_end_time(self):
        """Probar que duration_hours es 0 sin end_time"""
        time_log = TaskTimeLogFactory(end_time=None)
        assert time_log.duration_hours == 0

    def test_duration_hours_less_than_hour(self):
        """Probar cálculo de duración menor a una hora"""
        start = timezone.now()
        end = start + timedelta(minutes=30)

        time_log = TaskTimeLogFactory(start_time=start, end_time=end)
        # 0.5 horas
        assert abs(time_log.duration_hours - 0.5) < 0.01


@pytest.mark.django_db
@pytest.mark.models
class TestTaskTimeLogRelationships:
    """Pruebas de relaciones de TaskTimeLog"""

    def test_time_log_task_relationship(self):
        """Probar relación con Task"""
        task = TaskFactory()
        time_log = TaskTimeLogFactory(task=task)

        assert time_log.task == task
        assert time_log in task.time_logs.all()

    def test_time_log_employee_relationship(self):
        """Probar relación con Employee"""
        employee = EmployeeFactory()
        time_log = TaskTimeLogFactory(employee=employee)

        assert time_log.employee == employee
        assert time_log in employee.time_logs.all()

    def test_time_log_task_cascade_delete(self):
        """Probar que al eliminar Task se eliminan los time_logs"""
        task = TaskFactory()
        time_log1 = TaskTimeLogFactory(task=task)
        time_log2 = TaskTimeLogFactory(task=task)

        task.delete()

        assert not TaskTimeLog.objects.filter(pk=time_log1.pk).exists()
        assert not TaskTimeLog.objects.filter(pk=time_log2.pk).exists()

    def test_time_log_employee_cascade_delete(self):
        """Probar que al eliminar Employee se eliminan los time_logs"""
        employee = EmployeeFactory()
        time_log1 = TaskTimeLogFactory(employee=employee)
        time_log2 = TaskTimeLogFactory(employee=employee)

        employee.delete()

        assert not TaskTimeLog.objects.filter(pk=time_log1.pk).exists()
        assert not TaskTimeLog.objects.filter(pk=time_log2.pk).exists()


@pytest.mark.django_db
@pytest.mark.models
class TestTaskComment:
    """Pruebas para el modelo TaskComment"""

    def test_comment_creation(self):
        """Probar creación básica de comentario"""
        comment = TaskCommentFactory()
        assert comment.pk is not None
        assert comment.task is not None
        assert comment.author is not None
        assert comment.content is not None

    def test_comment_str_representation(self):
        """Probar representación string del comentario"""
        task = TaskFactory(title="Tarea Importante")
        author = EmployeeUserFactory(username="juan")
        comment = TaskCommentFactory(task=task, author=author)
        expected = f"Tarea Importante - {author} - {comment.created_at.date()}"
        assert str(comment) == expected

    def test_comment_content_required(self):
        """Probar que content es requerido"""
        with pytest.raises(IntegrityError):
            TaskCommentFactory(content=None)

    def test_comment_is_internal_default(self):
        """Probar valor por defecto de is_internal"""
        comment = TaskCommentFactory()
        assert comment.is_internal is False

    def test_comment_is_internal_true(self):
        """Probar que is_internal puede ser True"""
        comment = TaskCommentFactory(is_internal=True)
        assert comment.is_internal is True

    def test_comment_ordering(self):
        """Probar ordenamiento por created_at descendente"""
        comment1 = TaskCommentFactory()
        comment2 = TaskCommentFactory()
        comment3 = TaskCommentFactory()

        comments = TaskComment.objects.all()
        # Deberían estar ordenados por created_at descendente
        assert comments[0].created_at >= comments[1].created_at
        assert comments[1].created_at >= comments[2].created_at


@pytest.mark.django_db
@pytest.mark.models
class TestTaskCommentRelationships:
    """Pruebas de relaciones de TaskComment"""

    def test_comment_task_relationship(self):
        """Probar relación con Task"""
        task = TaskFactory()
        comment1 = TaskCommentFactory(task=task)
        comment2 = TaskCommentFactory(task=task)

        assert comment1.task == task
        assert comment2.task == task
        assert comment1 in task.comments.all()
        assert comment2 in task.comments.all()

    def test_comment_author_relationship(self):
        """Probar relación con User (author)"""
        author = EmployeeUserFactory()
        comment1 = TaskCommentFactory(author=author)
        comment2 = TaskCommentFactory(author=author)

        assert comment1.author == author
        assert comment2.author == author
        assert comment1 in author.task_comments.all()
        assert comment2 in author.task_comments.all()

    def test_comment_task_cascade_delete(self):
        """Probar que al eliminar Task se eliminan los comentarios"""
        task = TaskFactory()
        comment1 = TaskCommentFactory(task=task)
        comment2 = TaskCommentFactory(task=task)

        task.delete()

        assert not TaskComment.objects.filter(pk=comment1.pk).exists()
        assert not TaskComment.objects.filter(pk=comment2.pk).exists()

    def test_comment_author_cascade_delete(self):
        """Probar que al eliminar User se eliminan los comentarios"""
        author = EmployeeUserFactory()
        comment1 = TaskCommentFactory(author=author)
        comment2 = TaskCommentFactory(author=author)

        author.delete()

        assert not TaskComment.objects.filter(pk=comment1.pk).exists()
        assert not TaskComment.objects.filter(pk=comment2.pk).exists()


@pytest.mark.django_db
@pytest.mark.models
class TestTaskCommentMultipleAuthors:
    """Pruebas con múltiples autores en comentarios"""

    def test_multiple_authors_same_task(self):
        """Probar que múltiples autores pueden comentar en la misma tarea"""
        task = TaskFactory()
        author1 = EmployeeUserFactory()
        author2 = AdminUserFactory()

        comment1 = TaskCommentFactory(task=task, author=author1)
        comment2 = TaskCommentFactory(task=task, author=author2)

        assert comment1.author != comment2.author
        assert comment1.task == comment2.task
        assert task.comments.count() == 2

    def test_same_author_multiple_comments(self):
        """Probar que un autor puede hacer múltiples comentarios"""
        task = TaskFactory()
        author = EmployeeUserFactory()

        comment1 = TaskCommentFactory(task=task, author=author)
        comment2 = TaskCommentFactory(task=task, author=author)

        assert comment1.author == comment2.author
        assert comment1.task == comment2.task
        assert author.task_comments.count() == 2


@pytest.mark.django_db
@pytest.mark.models
class TestTaskCommentInternalFlag:
    """Pruebas del flag is_internal"""

    def test_internal_comment_filtering(self):
        """Probar que se puede filtrar comentarios internos"""
        task = TaskFactory()
        internal_comment = TaskCommentFactory(task=task, is_internal=True)
        public_comment = TaskCommentFactory(task=task, is_internal=False)

        internal_comments = task.comments.filter(is_internal=True)
        public_comments = task.comments.filter(is_internal=False)

        assert internal_comment in internal_comments
        assert public_comment in public_comments
        assert internal_comment not in public_comments
        assert public_comment not in internal_comments

