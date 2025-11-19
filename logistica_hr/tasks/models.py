"""
Modelos para la aplicación tasks
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from logistica_hr.core.models import BaseModel
from logistica_hr.users.models import User
from logistica_hr.employees.models import Employee


class TaskCategory(BaseModel):
    """
    Modelo para categorías de tareas
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nombre')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_('Color')
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Prioridad')
    )

    class Meta:
        verbose_name = _('Categoría de Tarea')
        verbose_name_plural = _('Categorías de Tareas')
        ordering = ['priority', 'name']

    def __str__(self):
        return self.name


class Task(BaseModel):
    """
    Modelo principal para tareas
    """
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('in_progress', _('En Progreso')),
        ('completed', _('Completada')),
        ('cancelled', _('Cancelada')),
        ('on_hold', _('En Espera')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Baja')),
        ('medium', _('Media')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_('Título')
    )
    description = models.TextField(
        verbose_name=_('Descripción')
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('Categoría')
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name=_('Asignado a')
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name=_('Asignado por')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Estado')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Prioridad')
    )
    due_date = models.DateTimeField(
        verbose_name=_('Fecha de Vencimiento')
    )
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Horas Estimadas')
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Horas Reales')
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Inicio')
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Completado')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )

    class Meta:
        verbose_name = _('Tarea')
        verbose_name_plural = _('Tareas')
        ordering = ['-due_date', 'priority']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.assigned_to}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status not in ['completed', 'cancelled']

    @property
    def progress_percentage(self):
        if self.estimated_hours and self.actual_hours:
            return min(100, (self.actual_hours / self.estimated_hours) * 100)
        return 0

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completion_date:
            from django.utils import timezone
            self.completion_date = timezone.now()
        elif self.status == 'in_progress' and not self.start_date:
            from django.utils import timezone
            self.start_date = timezone.now()
        super().save(*args, **kwargs)


class TaskTimeLog(BaseModel):
    """
    Modelo para registrar tiempo dedicado a tareas
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='time_logs',
        verbose_name=_('Tarea')
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='time_logs',
        verbose_name=_('Empleado')
    )
    start_time = models.DateTimeField(
        verbose_name=_('Hora de Inicio')
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Hora de Fin')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción del Trabajo')
    )
    is_break = models.BooleanField(
        default=False,
        verbose_name=_('Es Descanso')
    )

    class Meta:
        verbose_name = _('Registro de Tiempo')
        verbose_name_plural = _('Registros de Tiempo')
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.task.title} - {self.employee} - {self.start_time.date()}"

    @property
    def duration_hours(self):
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600
        return 0

    def save(self, *args, **kwargs):
        if self.end_time and self.end_time <= self.start_time:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        super().save(*args, **kwargs)


class TaskComment(BaseModel):
    """
    Modelo para comentarios en tareas
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Tarea')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        verbose_name=_('Autor')
    )
    content = models.TextField(
        verbose_name=_('Contenido')
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name=_('Es Interno')
    )

    class Meta:
        verbose_name = _('Comentario de Tarea')
        verbose_name_plural = _('Comentarios de Tareas')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.title} - {self.author} - {self.created_at.date()}"




