"""
Modelos para la aplicación employees
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from logistica_hr.core.models import BaseModel
from logistica_hr.users.models import User


class Department(BaseModel):
    """
    Modelo para departamentos de la empresa
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
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_('Gerente')
    )

    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(BaseModel):
    """
    Modelo para posiciones/cargos de empleados
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('Departamento')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Salario Base')
    )

    class Meta:
        verbose_name = _('Posición')
        verbose_name_plural = _('Posiciones')
        unique_together = ['name', 'department']
        ordering = ['department', 'name']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class Employee(BaseModel):
    """
    Modelo principal para empleados
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name=_('Usuario')
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('ID de Empleado')
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_('Posición')
    )
    hire_date = models.DateField(
        verbose_name=_('Fecha de Contratación')
    )
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_employees',
        verbose_name=_('Supervisor')
    )
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Contacto de Emergencia')
    )
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono de Emergencia')
    )
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Habilidades')
    )
    certifications = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Certificaciones')
    )

    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def department(self):
        return self.position.department if self.position else None

    @property
    def years_of_service(self):
        from datetime import date
        today = date.today()
        return today.year - self.hire_date.year - (
            (today.month, today.day) < (self.hire_date.month, self.hire_date.day)
        )


class WorkSchedule(BaseModel):
    """
    Modelo para horarios de trabajo
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name=_('Empleado')
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, _('Lunes')),
            (1, _('Martes')),
            (2, _('Miércoles')),
            (3, _('Jueves')),
            (4, _('Viernes')),
            (5, _('Sábado')),
            (6, _('Domingo')),
        ],
        verbose_name=_('Día de la Semana')
    )
    start_time = models.TimeField(
        verbose_name=_('Hora de Inicio')
    )
    end_time = models.TimeField(
        verbose_name=_('Hora de Fin')
    )
    break_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Inicio de Descanso')
    )
    break_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Fin de Descanso')
    )

    class Meta:
        verbose_name = _('Horario de Trabajo')
        verbose_name_plural = _('Horarios de Trabajo')
        unique_together = ['employee', 'day_of_week']
        ordering = ['employee', 'day_of_week']

    def __str__(self):
        return f"{self.employee} - {self.get_day_of_week_display()}"

    @property
    def total_hours(self):
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600


