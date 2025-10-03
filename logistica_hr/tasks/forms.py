from django import forms
from django.utils import timezone
from .models import Task, TaskCategory
from logistica_hr.employees.models import Employee

# Formatos aceptados para DateTime local (coincidir con <input type="datetime-local">)
_DT_INPUT_FORMATS = ['%Y-%m-%dT%H:%M', '%d-%m-%Y %H:%M', '%d/%m/%Y %H:%M']


def _employee_label(emp: Employee) -> str:
    """
    Etiqueta de empleado: 'Nombre Apellido (EMPxxxx)' si existe employee_id,
    si no, solo el nombre completo o el username.
    """
    full_name = emp.user.get_full_name() or emp.user.username
    return f"{full_name} ({emp.employee_id})" if getattr(emp, "employee_id", None) else full_name


class BaseTaskForm(forms.ModelForm):
    """
    Base para formularios de Task:
    - due_date con <input type="datetime-local"> y múltiples formatos.
    - set_assigned_by para que la vista inyecte el asignador.
    - save(assigned_by=...) para setear 'assigned_by' de forma segura.
    - Widgets/labels/help texts y estilo Bootstrap.
    """

    # Como en tu modelo due_date es DateTimeField, usamos DateTimeField aquí
    due_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=_DT_INPUT_FORMATS,
        label="Fecha de vencimiento",
        help_text="Selecciona fecha y hora local en que debe estar lista."
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'due_date', 'category',
            'assigned_to', 'status', 'template', 'estimated_hours'
        ]
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'priority': 'Prioridad',
            'category': 'Categoría',
            'assigned_to': 'Asignar a empleado',
            'status': 'Estado',
            'template': 'Guardar como plantilla',
            'estimated_hours': 'Horas estimadas',
        }
        help_texts = {
            'template': 'Si marcas esta opción, se guardará como plantilla reutilizable (no se asigna a nadie).',
            'estimated_hours': 'Opcional. Útil para métricas (ej. 1.5 = 1h 30m).',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título de la tarea', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe brevemente la tarea', 'rows': 3, 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estimated_hours': forms.NumberInput(attrs={'min': '0', 'step': '0.25', 'placeholder': 'Opcional', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        - Oculta 'category' si no hay categorías creadas.
        - Rellena y ordena 'assigned_to' (solo empleados).
        - Placeholders y defaults de UX.
        """
        super().__init__(*args, **kwargs)

        # Ocultar categoría si no existen
        if 'category' in self.fields and not TaskCategory.objects.exists():
            self.fields.pop('category')

        # Selector de empleado (solo rol 'employee'), ordenado por nombre y employee_id
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = (
                Employee.objects
                .filter(user__role='employee')
                .select_related('user')
                .order_by('user__first_name', 'user__last_name', 'employee_id')
            )
            self.fields['assigned_to'].label_from_instance = _employee_label

        # Placeholders/estética
        if 'title' in self.fields:
            self.fields['title'].widget.attrs.setdefault('placeholder', 'Título de la tarea')
        if 'description' in self.fields:
            self.fields['description'].widget.attrs.setdefault('placeholder', 'Descripción breve')

        # Si quieres inicializar due_date a +2h desde ahora (sugerencia UX), descomenta:
        # if not self.initial.get('due_date') and not self.instance.pk:
        #     local_now = timezone.localtime()
        #     self.initial['due_date'] = (local_now + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')

    # Validación opcional: no permitir due_date en el pasado
    def clean_due_date(self):
        dt = self.cleaned_data.get('due_date')
        if dt and dt < timezone.now():
            raise forms.ValidationError("La fecha/hora de vencimiento no puede estar en el pasado.")
        return dt

    def set_assigned_by(self, user):
        self.instance.assigned_by = user

    def save(self, assigned_by=None, commit=True):
        if assigned_by is not None:
            self.instance.assigned_by = assigned_by
        obj = super().save(commit=False)
        # Valida reglas del modelo (incluye 'La tarea debe tener un asignador.')
        obj.full_clean()
        if commit:
            obj.save()
        return obj


class AdminTaskForm(BaseTaskForm):
    """
    Admin → puede ver 'template' y 'status'.
    (No cambios extra: hereda todo de BaseTaskForm)
    """
    pass


class SupervisorTaskForm(BaseTaskForm):
    """
    Supervisor → NO muestra 'template'. Opcionalmente se le puede ocultar 'status'
    si quieres que siempre cree en 'pending'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Oculta 'Guardar como plantilla' para supervisores
        if 'template' in self.fields:
            self.fields.pop('template')

        # Si NO quieres que el supervisor cambie el estado inicial, descomenta para ocultarlo:
        # if 'status' in self.fields:
        #     self.fields.pop('status')
