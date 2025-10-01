from django.db.models.signals import post_save
from django.dispatch import receiver

from logistica_hr.users.models import User
from logistica_hr.employees.models import Employee, Department
from datetime import date


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    """Auto-crea perfil Employee cuando el usuario tiene rol 'employee'."""
    if instance.role == 'employee':
        if hasattr(instance, 'employee_profile'):
            return  # Ya existe
        dept, _ = Department.objects.get_or_create(
            name='General',
            defaults={'description': 'Departamento por defecto'}
        )
        Employee.objects.create(
            user=instance,
            employee_id=f"EMP{instance.id:04d}",
            position=None,
            hire_date=date.today(),
            supervisor=None
        )
