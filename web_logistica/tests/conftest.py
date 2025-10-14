"""
Configuración global de pytest para el proyecto Logistica HR
"""

import pytest
import os
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Configurar Django para testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings_sqlite')
django.setup()

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configuración de la base de datos para testing"""
    pass


@pytest.fixture
def request_factory():
    """Factory para crear requests de prueba"""
    return RequestFactory()


@pytest.fixture
def admin_user(db):
    """Crear usuario administrador para pruebas"""
    return User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='testpass123',
        role='admin',
        first_name='Admin',
        last_name='Test'
    )


@pytest.fixture
def supervisor_user(db):
    """Crear usuario supervisor para pruebas"""
    return User.objects.create_user(
        username='supervisor_test',
        email='supervisor@test.com',
        password='testpass123',
        role='supervisor',
        first_name='Supervisor',
        last_name='Test'
    )


@pytest.fixture
def employee_user(db):
    """Crear usuario empleado para pruebas"""
    return User.objects.create_user(
        username='employee_test',
        email='employee@test.com',
        password='testpass123',
        role='employee',
        first_name='Employee',
        last_name='Test'
    )


@pytest.fixture
def authenticated_request(request_factory, admin_user):
    """Request autenticado para pruebas"""
    request = request_factory.get('/')
    request.user = admin_user
    return request


@pytest.fixture
def unauthenticated_request(request_factory):
    """Request no autenticado para pruebas"""
    request = request_factory.get('/')
    request.user = None
    return request
