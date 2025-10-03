"""
Modelos para la aplicación performance
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from logistica_hr.core.models import BaseModel
from logistica_hr.users.models import User
from logistica_hr.employees.models import Employee
from logistica_hr.tasks.models import Task


class PerformanceMetric(BaseModel):
    """
    Modelo para métricas de rendimiento
    """
    METRIC_TYPE_CHOICES = [
        ('productivity', _('Productividad')),
        ('quality', _('Calidad')),
        ('efficiency', _('Eficiencia')),
        ('attendance', _('Asistencia')),
        ('safety', _('Seguridad')),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPE_CHOICES,
        verbose_name=_('Tipo de Métrica')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    unit = models.CharField(
        max_length=50,
        verbose_name=_('Unidad de Medida')
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Valor Objetivo')
    )
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Valor Mínimo')
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Valor Máximo')
    )
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_('Peso')
    )

    class Meta:
        verbose_name = _('Métrica de Rendimiento')
        verbose_name_plural = _('Métricas de Rendimiento')
        ordering = ['metric_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_metric_type_display()})"


class EmployeePerformance(BaseModel):
    """
    Modelo para el rendimiento de empleados
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_records',
        verbose_name=_('Empleado')
    )
    date = models.DateField(
        verbose_name=_('Fecha')
    )
    metric = models.ForeignKey(
        PerformanceMetric,
        on_delete=models.CASCADE,
        related_name='employee_performances',
        verbose_name=_('Métrica')
    )
    actual_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Valor Real')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluated_performances',
        verbose_name=_('Evaluado por')
    )

    class Meta:
        verbose_name = _('Rendimiento de Empleado')
        verbose_name_plural = _('Rendimientos de Empleados')
        unique_together = ['employee', 'date', 'metric']
        ordering = ['-date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['metric', 'date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.metric.name} - {self.date}"

    @property
    def performance_score(self):
        """Calcula el puntaje de rendimiento basado en el valor objetivo"""
        if self.metric.target_value:
            if self.actual_value >= self.metric.target_value:
                return 100
            elif self.metric.min_value and self.actual_value < self.metric.min_value:
                return 0
            else:
                # Cálculo proporcional
                range_value = self.metric.target_value - self.metric.min_value
                actual_range = self.actual_value - self.metric.min_value
                return max(0, (actual_range / range_value) * 100)
        return None

    @property
    def is_above_target(self):
        """Verifica si el rendimiento está por encima del objetivo"""
        if self.metric.target_value:
            return self.actual_value >= self.metric.target_value
        return False


class DailyWorkLog(BaseModel):
    """
    Modelo para registro diario de trabajo
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='daily_work_logs',
        verbose_name=_('Empleado')
    )
    date = models.DateField(
        verbose_name=_('Fecha')
    )
    start_time = models.TimeField(
        verbose_name=_('Hora de Inicio')
    )
    end_time = models.TimeField(
        verbose_name=_('Hora de Fin')
    )
    total_break_time = models.DurationField(
        default=0,
        verbose_name=_('Tiempo Total de Descanso')
    )
    packages_processed = models.IntegerField(
        default=0,
        verbose_name=_('Paquetes Procesados')
    )
    trucks_received = models.IntegerField(
        default=0,
        verbose_name=_('Camiones Recibidos')
    )
    trucks_dispatched = models.IntegerField(
        default=0,
        verbose_name=_('Camiones Despachados')
    )
    quality_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_('Puntaje de Calidad')
    )
    safety_incidents = models.IntegerField(
        default=0,
        verbose_name=_('Incidentes de Seguridad')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )

    class Meta:
        verbose_name = _('Registro Diario de Trabajo')
        verbose_name_plural = _('Registros Diarios de Trabajo')
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date}"

    @property
    def total_work_time(self):
        """Calcula el tiempo total de trabajo"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        if end < start:
            end += timedelta(days=1)
        total_time = end - start
        return total_time - self.total_break_time

    @property
    def productivity_score(self):
        """Calcula un puntaje de productividad basado en métricas"""
        score = 0
        if self.packages_processed > 0:
            score += min(40, self.packages_processed * 2)  # Máximo 40 puntos
        if self.trucks_received > 0:
            score += min(30, self.trucks_received * 3)  # Máximo 30 puntos
        if self.trucks_dispatched > 0:
            score += min(30, self.trucks_dispatched * 3)  # Máximo 30 puntos
        return score

    @property
    def efficiency_percentage(self):
        """Calcula el porcentaje de eficiencia (tiempo de trabajo vs tiempo total)"""
        total_time = self.total_work_time
        if total_time.total_seconds() > 0:
            work_time = total_time - self.total_break_time
            return (work_time.total_seconds() / total_time.total_seconds()) * 100
        return 0


class PerformanceEvaluation(BaseModel):
    """
    Modelo para evaluaciones de rendimiento
    """
    EVALUATION_TYPE_CHOICES = [
        ('daily', _('Diaria')),
        ('weekly', _('Semanal')),
        ('monthly', _('Mensual')),
        ('quarterly', _('Trimestral')),
        ('annual', _('Anual')),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name=_('Empleado')
    )
    evaluation_type = models.CharField(
        max_length=20,
        choices=EVALUATION_TYPE_CHOICES,
        verbose_name=_('Tipo de Evaluación')
    )
    start_date = models.DateField(
        verbose_name=_('Fecha de Inicio')
    )
    end_date = models.DateField(
        verbose_name=_('Fecha de Fin')
    )
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Puntaje General')
    )
    strengths = models.TextField(
        blank=True,
        verbose_name=_('Fortalezas')
    )
    areas_for_improvement = models.TextField(
        blank=True,
        verbose_name=_('Áreas de Mejora')
    )
    recommendations = models.TextField(
        blank=True,
        verbose_name=_('Recomendaciones')
    )
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_evaluations',
        verbose_name=_('Evaluado por')
    )
    evaluation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de Evaluación')
    )

    class Meta:
        verbose_name = _('Evaluación de Rendimiento')
        verbose_name_plural = _('Evaluaciones de Rendimiento')
        ordering = ['-end_date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'evaluation_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_evaluation_type_display()} - {self.end_date}"

    @property
    def duration_days(self):
        """Calcula la duración en días de la evaluación"""
        return (self.end_date - self.start_date).days + 1




