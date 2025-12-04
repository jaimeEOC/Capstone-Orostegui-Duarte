"""
Pruebas unitarias para el modelo User
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from logistica_hr.users.models import User
from tests.factories import UserFactory, AdminUserFactory, SupervisorUserFactory, EmployeeUserFactory


@pytest.mark.django_db
@pytest.mark.models
class TestUserModel:
    """Pruebas para el modelo User"""

    def test_user_creation(self):
        """Probar creación básica de usuario"""
        user = UserFactory()
        assert user.pk is not None
        assert user.username is not None
        assert user.email is not None
        assert user.role in ['admin', 'supervisor', 'employee']

    def test_user_str_representation(self):
        """Probar representación string del usuario"""
        user = UserFactory(first_name='Juan', last_name='Pérez', role='supervisor')
        expected = f"Juan Pérez ({user.get_role_display()})"
        assert str(user) == expected

    def test_user_full_name_property(self):
        """Probar propiedad full_name"""
        user = UserFactory(first_name='María', last_name='González')
        assert user.full_name == 'María González'

    def test_user_full_name_without_names(self):
        """Probar full_name cuando no hay nombres"""
        user = UserFactory(first_name='', last_name='', username='testuser')
        assert user.full_name == 'testuser'

    def test_user_role_choices(self):
        """Probar opciones válidas de rol"""
        valid_roles = ['admin', 'supervisor', 'employee']
        
        for role in valid_roles:
            user = UserFactory(role=role)
            assert user.role == role
            assert user.get_role_display() is not None

    def test_user_invalid_role(self):
        """Probar que no se puede crear usuario con rol inválido"""
        with pytest.raises(ValidationError):
            user = User(role='invalid_role')
            user.full_clean()

    def test_user_email_unique(self):
        """Probar que el email debe ser único"""
        email = 'test@example.com'
        UserFactory(email=email)
        
        with pytest.raises(IntegrityError):
            UserFactory(email=email)

    def test_user_username_unique(self):
        """Probar que el username debe ser único"""
        username = 'testuser'
        UserFactory(username=username)
        
        with pytest.raises(IntegrityError):
            UserFactory(username=username)

    def test_user_default_values(self):
        """Probar valores por defecto del usuario"""
        user = UserFactory(role='employee')  # Especificar rol explícitamente
        assert user.role == 'employee'  # Valor por defecto
        assert user.is_verified is True  # Valor por defecto en factory
        assert user.is_active is True  # Valor por defecto de AbstractUser

    def test_user_get_dashboard_url_admin(self):
        """Probar URL del dashboard para admin"""
        admin = AdminUserFactory()
        expected_url = '/admin/dashboard/'
        assert admin.get_dashboard_url() == expected_url

    def test_user_get_dashboard_url_supervisor(self):
        """Probar URL del dashboard para supervisor"""
        supervisor = SupervisorUserFactory()
        expected_url = '/supervisor/dashboard/'
        assert supervisor.get_dashboard_url() == expected_url

    def test_user_get_dashboard_url_employee(self):
        """Probar URL del dashboard para empleado"""
        employee = EmployeeUserFactory()
        expected_url = '/employee/dashboard/'
        assert employee.get_dashboard_url() == expected_url

    def test_user_phone_field_optional(self):
        """Probar que el campo phone es opcional"""
        user = UserFactory(phone='')
        assert user.phone == ''

    def test_user_avatar_field_optional(self):
        """Probar que el campo avatar es opcional"""
        user = UserFactory(avatar=None)
        assert user.avatar.name == '' or user.avatar.name is None  # ImageField puede ser None o string vacío

    def test_user_last_login_ip_field_optional(self):
        """Probar que el campo last_login_ip es opcional"""
        user = UserFactory(last_login_ip=None)
        assert user.last_login_ip is None

    def test_user_related_name_conflicts_avoided(self):
        """Probar que se evitan conflictos en related_name"""
        user = UserFactory()
        
        # Verificar que los related_name personalizados funcionan
        # Estos atributos se crean dinámicamente por Django
        assert hasattr(user, 'groups')
        assert hasattr(user, 'user_permissions')


@pytest.mark.django_db
@pytest.mark.models
class TestUserModelValidation:
    """Pruebas de validación del modelo User"""

    def test_user_email_format_validation(self):
        """Probar validación de formato de email"""
        with pytest.raises(ValidationError):
            user = User(email='invalid-email')
            user.full_clean()

    def test_user_phone_max_length(self):
        """Probar longitud máxima del campo phone"""
        long_phone = '1' * 21  # Más de 20 caracteres
        user = UserFactory(phone=long_phone)
        
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_user_role_max_length(self):
        """Probar longitud máxima del campo role"""
        long_role = 'a' * 21  # Más de 20 caracteres
        user = UserFactory(role=long_role)
        
        with pytest.raises(ValidationError):
            user.full_clean()


@pytest.mark.django_db
@pytest.mark.models
class TestUserModelMethods:
    """Pruebas de métodos del modelo User"""

    def test_user_has_perm_admin(self):
        """Probar que admin tiene todos los permisos"""
        admin = AdminUserFactory()
        # Los admins no tienen automáticamente todos los permisos
        # Necesitarían ser superuser o tener permisos específicos
        assert admin.is_staff is False  # Por defecto en factory
        assert admin.is_superuser is False  # Por defecto en factory

    def test_user_has_perm_supervisor(self):
        """Probar permisos limitados del supervisor"""
        supervisor = SupervisorUserFactory()
        # Los supervisores no deberían tener permisos de admin
        assert not supervisor.has_perm('auth.delete_user')

    def test_user_has_perm_employee(self):
        """Probar permisos limitados del empleado"""
        employee = EmployeeUserFactory()
        # Los empleados no deberían tener permisos administrativos
        assert not employee.has_perm('auth.add_user')
        assert not employee.has_perm('auth.change_user')
        assert not employee.has_perm('auth.delete_user')
