"""
Pruebas unitarias para el formulario de registro
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from logistica_hr.users.forms import RegistrationForm

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.forms
class TestRegistrationForm:
    """Pruebas para el formulario de registro"""

    def test_form_valid_with_valid_data(self):
        """Probar que el formulario es válido con datos válidos"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            print(f"Form non_field_errors: {form.non_field_errors()}")
        assert form.is_valid()

    def test_password_confirmation_must_match(self):
        """Probar que las contraseñas deben coincidir"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "password456",  # Diferente
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "Las contraseñas no coinciden" in str(form.errors)

    def test_username_generated_automatically(self):
        """Probar que el username se genera automáticamente desde nombre y apellido"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()
        
        user = form.save()
        assert user.username is not None
        assert "juan" in user.username.lower()
        assert "pérez" in user.username.lower() or "perez" in user.username.lower()

    def test_email_required(self):
        """Probar que el email es requerido"""
        form_data = {
            "email": "",  # Vacío
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_email_format_validation(self):
        """Probar validación de formato de email"""
        form_data = {
            "email": "email_invalido",  # Formato inválido
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_first_name_optional(self):
        """Probar que el nombre es opcional (puede estar vacío)"""
        form_data = {
            "email": "test@example.com",
            "first_name": "",  # Vacío - debería ser válido
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        # El formulario debería ser válido incluso con first_name vacío
        assert form.is_valid()

    def test_last_name_optional(self):
        """Probar que el apellido es opcional (puede estar vacío)"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "",  # Vacío - debería ser válido
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        # El formulario debería ser válido incluso con last_name vacío
        assert form.is_valid()

    def test_role_required(self):
        """Probar que el rol es requerido"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "",  # Vacío
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "role" in form.errors

    def test_role_validation(self):
        """Probar validación de rol"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "invalid_role",  # Rol inválido
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "role" in form.errors

    def test_phone_required(self):
        """Probar que el teléfono es obligatorio"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "",  # Vacío - debería fallar
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors
        assert "obligatorio" in str(form.errors["phone"]).lower()

    def test_phone_chilean_format_validation(self):
        """Probar validación de formato de teléfono chileno"""
        # Teléfono que no empieza con 9
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "812345678",  # No empieza con 9
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors
        assert "comenzar con 9" in str(form.errors["phone"]).lower()
    
    def test_phone_length_validation(self):
        """Probar validación de longitud de teléfono"""
        # Teléfono con menos de 9 dígitos
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "91234567",  # Solo 8 dígitos
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors
        
        # Teléfono con más de 9 dígitos
        form_data["phone"] = "9123456789"  # 10 dígitos
        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors
    
    def test_phone_numeric_only(self):
        """Probar que el teléfono solo acepta números"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "91234567a",  # Contiene letra
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors
        assert "números" in str(form.errors["phone"]).lower() or "números" in str(form.errors["phone"]).lower()

    def test_weak_password_validation(self):
        """Probar validación de contraseña débil"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "123",  # Muy débil
            "password2": "123",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        # Debería mostrar error de contraseña débil

    def test_password_too_short(self):
        """Probar contraseña muy corta"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "ab",  # Muy corta
            "password2": "ab",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()

    def test_password_common_sequence(self):
        """Probar contraseña con secuencia común"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "12345678",  # Secuencia común
            "password2": "12345678",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()

    def test_duplicate_email_validation(self):
        """Probar validación de email duplicado"""
        # Crear usuario existente
        existing_user = User.objects.create_user(
            username="existing",
            email="existente@test.com",
            password="MySecurePass123!"
        )
        
        form_data = {
            "email": "existente@test.com",  # Duplicado
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
        assert "ya existe" in str(form.errors["email"]).lower()

    def test_valid_admin_role(self):
        """Probar rol de admin válido"""
        form_data = {
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()

    def test_valid_supervisor_role(self):
        """Probar rol de supervisor válido"""
        form_data = {
            "email": "supervisor@example.com",
            "first_name": "Supervisor",
            "last_name": "User",
            "role": "supervisor",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()

    def test_valid_employee_role(self):
        """Probar rol de empleado válido"""
        form_data = {
            "email": "employee@example.com",
            "first_name": "Employee",
            "last_name": "User",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()

    def test_form_save_creates_user(self):
        """Probar que el formulario crea usuario al guardar"""
        form_data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()

        user = form.save()
        # Verificar que el username se generó automáticamente
        assert user.username is not None
        assert "new" in user.username.lower()
        assert "user" in user.username.lower()
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.role == "employee"
        assert user.phone == "912345678"
        assert user.check_password("MySecurePass123!")

    def test_form_save_with_commit_false(self):
        """Probar que el formulario no guarda en BD con commit=False"""
        form_data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()

        user = form.save(commit=False)
        assert user.username is not None
        assert "new" in user.username.lower()
        assert not User.objects.filter(email="new@example.com").exists()

    def test_form_clean_email_strips_whitespace_and_lowercase(self):
        """Probar que clean_email elimina espacios y convierte a minúsculas"""
        form_data = {
            "email": "  TEST@EXAMPLE.COM  ",  # Con espacios y mayúsculas
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["email"] == "test@example.com"

    def test_form_clean_phone_strips_whitespace(self):
        """Probar que clean_phone elimina espacios en blanco"""
        form_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "  912345678  ",  # Con espacios
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["phone"] == "912345678"

    def test_form_clean_email_empty_string(self):
        """Probar que clean_email maneja string vacío"""
        form_data = {
            "email": "",  # Vacío
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }

        form = RegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
    
    def test_username_generation_with_duplicate(self):
        """Probar que el username se genera con contador si hay duplicados"""
        # Crear primer usuario
        form_data1 = {
            "email": "user1@test.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345678",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }
        form1 = RegistrationForm(data=form_data1)
        assert form1.is_valid()
        user1 = form1.save()
        
        # Crear segundo usuario con mismo nombre y apellido
        form_data2 = {
            "email": "user2@test.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "role": "employee",
            "phone": "912345679",
            "password1": "MySecurePass123!",
            "password2": "MySecurePass123!",
        }
        form2 = RegistrationForm(data=form_data2)
        assert form2.is_valid()
        user2 = form2.save()
        
        # Verificar que tienen usernames diferentes
        assert user1.username != user2.username
        # El segundo debería tener un contador
        assert user2.username.endswith("2") or user1.username.endswith("1")
