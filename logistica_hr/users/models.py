"""
Modelos para la aplicación users
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuario personalizado con roles específicos
    """
    ROLE_CHOICES = [
        ('admin', _('Administrador')),
        ('supervisor', _('Supervisor')),
        ('employee', _('Empleado')),
    ]

    email = models.EmailField(
        unique=True,
        verbose_name=_('Correo Electrónico')
    )
    
    # Sobrescribir campos para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="logistica_users",
        related_query_name="logistica_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="logistica_users",
        related_query_name="logistica_user",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name=_('Rol')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('Avatar')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verificado')
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Última IP de Login')
    )

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['username']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_role_display(self):
        """Retorna el nombre del rol en español"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == 'admin'

    def is_supervisor(self):
        """Verifica si el usuario es supervisor"""
        return self.role == 'supervisor'

    def is_employee(self):
        """Verifica si el usuario es empleado"""
        return self.role == 'employee'

    def can_manage_users(self):
        """Verifica si el usuario puede gestionar otros usuarios"""
        return self.role in ['admin', 'supervisor']

    def can_view_reports(self):
        """Verifica si el usuario puede ver reportes"""
        return self.role in ['admin', 'supervisor']

    def can_manage_employees(self):
        """Verifica si el usuario puede gestionar empleados"""
        return self.role in ['admin', 'supervisor']

    def get_dashboard_url(self):
        """Retorna la URL del dashboard según el rol"""
        if self.is_admin():
            return '/admin/dashboard/'
        elif self.is_supervisor():
            return '/supervisor/dashboard/'
        else:
            return '/employee/dashboard/'
