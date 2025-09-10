"""
Modelos para la aplicación reports
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from logistica_hr.core.models import BaseModel
from logistica_hr.users.models import User


class ReportTemplate(BaseModel):
    """
    Modelo para plantillas de reportes
    """
    REPORT_TYPE_CHOICES = [
        ('productivity', _('Productividad')),
        ('performance', _('Rendimiento')),
        ('attendance', _('Asistencia')),
        ('quality', _('Calidad')),
        ('safety', _('Seguridad')),
        ('custom', _('Personalizado')),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name=_('Tipo de Reporte')
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='pdf',
        verbose_name=_('Formato')
    )
    template_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Configuración de Plantilla')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
    )

    class Meta:
        verbose_name = _('Plantilla de Reporte')
        verbose_name_plural = _('Plantillas de Reportes')
        ordering = ['report_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class ScheduledReport(BaseModel):
    """
    Modelo para reportes programados
    """
    FREQUENCY_CHOICES = [
        ('daily', _('Diario')),
        ('weekly', _('Semanal')),
        ('monthly', _('Mensual')),
        ('quarterly', _('Trimestral')),
        ('annual', _('Anual')),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='scheduled_reports',
        verbose_name=_('Plantilla')
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name=_('Frecuencia')
    )
    recipients = models.JSONField(
        default=list,
        verbose_name=_('Destinatarios')
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Parámetros')
    )
    last_generated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Última Generación')
    )
    next_generation = models.DateTimeField(
        verbose_name=_('Próxima Generación')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
    )

    class Meta:
        verbose_name = _('Reporte Programado')
        verbose_name_plural = _('Reportes Programados')
        ordering = ['-next_generation']

    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


class GeneratedReport(BaseModel):
    """
    Modelo para reportes generados
    """
    STATUS_CHOICES = [
        ('generating', _('Generando')),
        ('completed', _('Completado')),
        ('failed', _('Fallido')),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name=_('Plantilla')
    )
    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        verbose_name=_('Reporte Programado')
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        verbose_name=_('Generado por')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='generating',
        verbose_name=_('Estado')
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Parámetros Utilizados')
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Ruta del Archivo')
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Tamaño del Archivo (bytes)')
    )
    generation_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name=_('Tiempo de Generación')
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_('Mensaje de Error')
    )

    class Meta:
        verbose_name = _('Reporte Generado')
        verbose_name_plural = _('Reportes Generados')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['template', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.created_at.date()}"

    @property
    def file_size_mb(self):
        """Retorna el tamaño del archivo en MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def is_successful(self):
        """Verifica si el reporte se generó exitosamente"""
        return self.status == 'completed' and bool(self.file_path)


class ReportParameter(BaseModel):
    """
    Modelo para parámetros de reportes
    """
    PARAMETER_TYPE_CHOICES = [
        ('date', _('Fecha')),
        ('date_range', _('Rango de Fechas')),
        ('employee', _('Empleado')),
        ('department', _('Departamento')),
        ('metric', _('Métrica')),
        ('text', _('Texto')),
        ('number', _('Número')),
        ('boolean', _('Booleano')),
        ('choice', _('Selección')),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre')
    )
    display_name = models.CharField(
        max_length=100,
        verbose_name=_('Nombre de Visualización')
    )
    parameter_type = models.CharField(
        max_length=20,
        choices=PARAMETER_TYPE_CHOICES,
        verbose_name=_('Tipo de Parámetro')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_('Requerido')
    )
    default_value = models.TextField(
        blank=True,
        verbose_name=_('Valor por Defecto')
    )
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Reglas de Validación')
    )
    choices = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Opciones de Selección')
    )

    class Meta:
        verbose_name = _('Parámetro de Reporte')
        verbose_name_plural = _('Parámetros de Reportes')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_parameter_type_display()})"




