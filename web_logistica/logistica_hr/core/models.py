"""
Modelos base para el proyecto Logistica HR
Siguiendo las mejores prácticas del Django Styleguide
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Modelo base que incluye campos comunes para todos los modelos
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} - {self.pk}"


class TimestampedModel(models.Model):
    """
    Modelo base solo con timestamps
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

