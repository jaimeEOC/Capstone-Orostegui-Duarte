"""
Formularios para la aplicación users
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """
    Formulario de registro de usuarios
    """
    username = forms.CharField(widget=forms.HiddenInput(), required=False)

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
        fields = ["email", "first_name", "last_name", "role", "phone"]
        widgets = {
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
                    "placeholder": "912345678",
                    "id": "id_phone",
                    "maxlength": "9",
                    "inputmode": "numeric",
                    "pattern": "9\\d{8}",  # Regex HTML
                    "title": "Debe comenzar con 9 y tener 9 dígitos"
                }
            ),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if not email:
            raise ValidationError("El correo es obligatorio.")

        # Buscar en la BD si ya existe ese correo
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(
                "Ya existe una cuenta registrada con este correo."
            )

        return email

    def clean_phone(self):
        """Teléfono chileno: exactamente 9 dígitos y comienza con 9."""
        phone = (self.cleaned_data.get("phone") or "").strip()

        # Teléfono es obligatorio
        if not phone:
            raise ValidationError("El teléfono es obligatorio.")

        # Solo números
        if not phone.isdigit():
            raise ValidationError("El teléfono solo debe contener números.")

        # Largo exacto
        if len(phone) != 9:
            raise ValidationError("El teléfono debe tener exactamente 9 dígitos.")

        # Celular chileno: debe empezar con 9
        if not phone.startswith("9"):
            raise ValidationError("El teléfono debe comenzar con 9.")

        return phone



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
        user = super().save(commit=False)

        first = self.cleaned_data["first_name"].strip().lower()
        last = self.cleaned_data["last_name"].strip().lower()

        base_username = f"{first}.{last}".replace(" ", "")

        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{base_username}{counter}"

        user.username = username
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserEditForm(forms.ModelForm):
    """
    Formulario para editar usuarios (sin contraseña obligatoria)
    """
    
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "phone"]
        widgets = {
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
                    "placeholder": "912345678",
                    "id": "id_phone",
                    "maxlength": "9",
                    "inputmode": "numeric",
                    "pattern": "9\\d{8}",
                    "title": "Debe comenzar con 9 y tener 9 dígitos"
                }
            ),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if not email:
            raise ValidationError("El correo es obligatorio.")

        # Buscar duplicado
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Ya existe una cuenta registrada con este correo.")

        return email


    def clean_phone(self):
        """Teléfono chileno: exactamente 9 dígitos y comienza con 9."""
        phone = (self.cleaned_data.get("phone") or "").strip()

        # Teléfono es obligatorio
        if not phone:
            raise ValidationError("El teléfono es obligatorio.")

        # Solo números
        if not phone.isdigit():
            raise ValidationError("El teléfono solo debe contener números.")

        # Largo exacto
        if len(phone) != 9:
            raise ValidationError("El teléfono debe tener exactamente 9 dígitos.")

        # Celular chileno: debe empezar con 9
        if not phone.startswith("9"):
            raise ValidationError("El teléfono debe comenzar con 9.")

        return phone

