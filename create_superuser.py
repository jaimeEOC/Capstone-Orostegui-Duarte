#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings_sqlite')
django.setup()

from django.contrib.auth import get_user_model
from logistica_hr.employees.models import Department, Position, Employee

User = get_user_model()

def create_users():
    """Crear usuarios de prueba con diferentes roles"""
    
    # Crear administrador
    if not User.objects.filter(username='admin').exists():
        admin_user = User(
            username='admin',
            email='admin@logistica.com',
            first_name='Administrador',
            last_name='Sistema',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Administrador 'admin' creado exitosamente")
    else:
        admin_user = User.objects.get(username='admin')
        print("ℹ️  El administrador 'admin' ya existe")
    
    # Crear supervisor
    if not User.objects.filter(username='supervisor').exists():
        supervisor_user = User(
            username='supervisor',
            email='supervisor@logistica.com',
            first_name='Carlos',
            last_name='Supervisor',
            role='supervisor',
            phone='+56912345678'
        )
        supervisor_user.set_password('supervisor123')
        supervisor_user.save()
        print("✅ Supervisor 'supervisor' creado exitosamente")
    else:
        supervisor_user = User.objects.get(username='supervisor')
        print("ℹ️  El supervisor 'supervisor' ya existe")
    
    # Crear empleado
    if not User.objects.filter(username='empleado').exists():
        empleado_user = User(
            username='empleado',
            email='empleado@logistica.com',
            first_name='María',
            last_name='Empleada',
            role='employee',
            phone='+56987654321'
        )
        empleado_user.set_password('empleado123')
        empleado_user.save()
        print("✅ Empleado 'empleado' creado exitosamente")
    else:
        empleado_user = User.objects.get(username='empleado')
        print("ℹ️  El empleado 'empleado' ya existe")
    
    # Crear departamentos de prueba
    create_departments_and_positions(admin_user, supervisor_user, empleado_user)

def create_departments_and_positions(admin_user, supervisor_user, empleado_user):
    """Crear departamentos y posiciones de prueba"""
    
    # Crear departamento de Logística
    dept_logistica, created = Department.objects.get_or_create(
        name='Logística',
        defaults={
            'description': 'Departamento encargado de la gestión de almacén y distribución',
            'manager': admin_user
        }
    )
    if created:
        print("✅ Departamento 'Logística' creado")
    
    # Crear departamento de Recursos Humanos
    dept_rrhh, created = Department.objects.get_or_create(
        name='Recursos Humanos',
        defaults={
            'description': 'Departamento de gestión de personal',
            'manager': admin_user
        }
    )
    if created:
        print("✅ Departamento 'Recursos Humanos' creado")
    
    # Crear posiciones
    pos_supervisor, created = Position.objects.get_or_create(
        name='Supervisor de Logística',
        department=dept_logistica,
        defaults={
            'description': 'Supervisor encargado del equipo de logística',
            'base_salary': 800000
        }
    )
    if created:
        print("✅ Posición 'Supervisor de Logística' creada")
    
    pos_operario, created = Position.objects.get_or_create(
        name='Operario de Almacén',
        department=dept_logistica,
        defaults={
            'description': 'Operario encargado del manejo de paquetes y camiones',
            'base_salary': 500000
        }
    )
    if created:
        print("✅ Posición 'Operario de Almacén' creada")
    
    # Crear perfiles de empleados
    create_employee_profiles(supervisor_user, empleado_user, pos_supervisor, pos_operario)

def create_employee_profiles(supervisor_user, empleado_user, pos_supervisor, pos_operario):
    """Crear perfiles de empleados"""
    
    # Perfil del supervisor
    if not hasattr(supervisor_user, 'employee_profile'):
        Employee.objects.create(
            user=supervisor_user,
            employee_id='SUP001',
            position=pos_supervisor,
            hire_date='2024-01-15',
            emergency_contact='Ana Supervisor',
            emergency_phone='+56911111111',
            skills=['Liderazgo', 'Gestión de equipos', 'Logística'],
            certifications=['Certificación en Logística', 'Curso de Supervisión']
        )
        print("✅ Perfil de empleado para supervisor creado")
    
    # Perfil del empleado
    if not hasattr(empleado_user, 'employee_profile'):
        Employee.objects.create(
            user=empleado_user,
            employee_id='EMP001',
            position=pos_operario,
            hire_date='2024-02-01',
            supervisor=supervisor_user,
            emergency_contact='Juan Empleado',
            emergency_phone='+56922222222',
            skills=['Manejo de paquetes', 'Operación de montacargas', 'Atención al detalle'],
            certifications=['Licencia de montacargas', 'Curso de seguridad']
        )
        print("✅ Perfil de empleado para operario creado")

if __name__ == '__main__':
    print("🚀 Creando usuarios de prueba...")
    create_users()
    print("\n📋 Credenciales de acceso:")
    print("👑 Administrador: admin / admin123")
    print("👨‍💼 Supervisor: supervisor / supervisor123")
    print("👷 Empleado: empleado / empleado123")
    print("\n✨ ¡Usuarios creados exitosamente!")
