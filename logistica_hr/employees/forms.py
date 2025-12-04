"""
Formularios para la aplicación employees
"""

from django import forms
from .models import Employee


class EmployeeEditForm(forms.ModelForm):
    """
    Formulario para editar empleados (solo campos esenciales)
    """
    
    class Meta:
        model = Employee
        fields = ["supervisor"]
        widgets = {
            "supervisor": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_supervisor",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar supervisores disponibles
        from logistica_hr.users.models import User
        self.fields['supervisor'].queryset = User.objects.filter(role='supervisor').order_by('first_name', 'last_name')
        self.fields['supervisor'].required = False

