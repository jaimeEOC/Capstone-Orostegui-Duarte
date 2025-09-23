#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings_sqlite')
django.setup()

from django.contrib.auth import get_user_model
from logistica_hr.employees.models import Department, Position, Employee

User = get_user_model()

def reset_database():
    """Limpiar y recrear la base de datos"""
    
    print("🗑️  Limpiando base de datos...")
    
    # Eliminar todos los usuarios
    User.objects.all().delete()
    print("✅ Usuarios eliminados")
    
    # Eliminar todos los empleados
    Employee.objects.all().delete()
    print("✅ Empleados eliminados")
    
    # Eliminar todas las posiciones
    Position.objects.all().delete()
    print("✅ Posiciones eliminadas")
    
    # Eliminar todos los departamentos
    Department.objects.all().delete()
    print("✅ Departamentos eliminados")
    
    print("\n🚀 Creando usuarios de prueba...")
    
    # Crear administrador
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
    print("✅ Administrador 'admin' creado")
    
    # Crear supervisor
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
    print("✅ Supervisor 'supervisor' creado")
    
    # Crear empleado
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
    print("✅ Empleado 'empleado' creado")
    
    # Crear departamentos
    dept_logistica = Department.objects.create(
        name='Logística',
        description='Departamento encargado de la gestión de almacén y distribución',
        manager=admin_user
    )
    print("✅ Departamento 'Logística' creado")
    
    dept_rrhh = Department.objects.create(
        name='Recursos Humanos',
        description='Departamento de gestión de personal',
        manager=admin_user
    )
    print("✅ Departamento 'Recursos Humanos' creado")
    
    # Crear posiciones
    pos_supervisor = Position.objects.create(
        name='Supervisor de Logística',
        department=dept_logistica,
        description='Supervisor encargado del equipo de logística',
        base_salary=800000
    )
    print("✅ Posición 'Supervisor de Logística' creada")
    
    pos_operario = Position.objects.create(
        name='Operario de Almacén',
        department=dept_logistica,
        description='Operario encargado del manejo de paquetes y camiones',
        base_salary=500000
    )
    print("✅ Posición 'Operario de Almacén' creada")
    
    # Crear perfiles de empleados
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
    
    print("\n📋 Credenciales de acceso:")
    print("👑 Administrador: admin / admin123")
    print("👨‍💼 Supervisor: supervisor / supervisor123")
    print("👷 Empleado: empleado / empleado123")
    print("\n✨ ¡Base de datos reiniciada exitosamente!")

if __name__ == '__main__':
    reset_database()
