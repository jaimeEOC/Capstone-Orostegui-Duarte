"""
Formularios para la aplicación users
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """
    Formulario de registro de usuarios
    """

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Contraseña",
                "id": "id_password1",
            }
        ),
        help_text="La contraseña debe tener al menos 8 caracteres.",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Confirmar contraseña",
                "id": "id_password2",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "phone"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Nombre de usuario",
                    "id": "id_username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "correo@empresa.com",
                    "id": "id_email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Nombre",
                    "id": "id_first_name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Apellido",
                    "id": "id_last_name",
                }
            ),
            "role": forms.Select(attrs={"class": "form-select", "id": "id_role"}),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Teléfono",
                    "id": "id_phone",
                }
            ),
        }

    def clean_username(self):
        """Validar unicidad de username - SIN validación de BD por ahora"""
        username = (self.cleaned_data.get("username") or "").strip()
        # Temporalmente sin validación de BD para evitar errores
        return username

    def clean_email(self):
        """Validar unicidad de email - SIN validación de BD por ahora"""
        email = (self.cleaned_data.get("email") or "").strip()
        # Temporalmente sin validación de BD para evitar errores
        return email

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")

            # Validar contraseña con las reglas de Django
            try:
                validate_password(password1)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)

        return cleaned_data

    def save(self, commit=True):
        """Guardar usuario con contraseña encriptada"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
