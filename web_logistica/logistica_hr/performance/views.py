"""
Vistas para la aplicación performance
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import date, timedelta

from logistica_hr.employees.models import Employee
from .models import DailyWorkLog


class DailyWorkLogForm(forms.ModelForm):
    """Formulario para registrar trabajo diario"""
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'placeholder': 'Seleccione la fecha'
        }),
        label='Fecha',
        initial=date.today
    )
    
    # Campos separados para hora de inicio (más user-friendly)
    start_hour = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '23',
            'placeholder': '08'
        }),
        label='Hora de Inicio',
        required=True
    )
    
    start_minute = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '59',
            'placeholder': '00'
        }),
        label='Minuto',
        required=True
    )
    
    # Campos separados para hora de fin (más user-friendly)
    end_hour = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '23',
            'placeholder': '17'
        }),
        label='Hora de Fin',
        required=True
    )
    
    end_minute = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '59',
            'placeholder': '00'
        }),
        label='Minuto',
        required=True
    )
    
    # Campos separados para tiempo de descanso (más user-friendly)
    break_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '23',
            'placeholder': '0'
        }),
        label='Horas de Descanso',
        required=False,
        initial=0
    )
    
    break_minutes = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'max': '59',
            'placeholder': '0'
        }),
        label='Minutos de Descanso',
        required=False,
        initial=0
    )
    
    class Meta:
        model = DailyWorkLog
        fields = [
            'date',
            'packages_processed', 'trucks_received', 'trucks_dispatched',
            'quality_score', 'safety_incidents', 'notes'
        ]
        widgets = {
            'packages_processed': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'trucks_received': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'trucks_dispatched': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'quality_score': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0', 
                'max': '7', 
                'step': '0.01',
                'placeholder': '0.00 - 7.00'
            }),
            'safety_incidents': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
        labels = {
            'packages_processed': 'Paquetes Procesados',
            'trucks_received': 'Camiones Recibidos',
            'trucks_dispatched': 'Camiones Despachados',
            'quality_score': 'Puntaje de Calidad (0.0 - 7.0)',
            'safety_incidents': 'Incidentes de Seguridad',
            'notes': 'Notas',
        }
        help_texts = {
            'quality_score': 'Puntaje de calidad entre 0.0 y 7.0',
        }
    
    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Si hay una instancia, cargar horas y minutos desde start_time y end_time
        if instance:
            if instance.start_time:
                self.fields['start_hour'].initial = instance.start_time.hour
                self.fields['start_minute'].initial = instance.start_time.minute
            
            if instance.end_time:
                self.fields['end_hour'].initial = instance.end_time.hour
                self.fields['end_minute'].initial = instance.end_time.minute
            
            # Cargar break_hours y break_minutes desde total_break_time
            if instance.total_break_time:
                total_seconds = int(instance.total_break_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                self.fields['break_hours'].initial = hours
                self.fields['break_minutes'].initial = minutes
        
        # Hacer campos opcionales
        self.fields['quality_score'].required = False
        self.fields['notes'].required = False
    
    def clean(self):
        from datetime import time as time_class
        
        cleaned_data = super().clean()
        log_date = cleaned_data.get('date')
        
        # Obtener horas y minutos de inicio
        start_hour = cleaned_data.get('start_hour')
        start_minute = cleaned_data.get('start_minute', 0) or 0
        
        # Obtener horas y minutos de fin
        end_hour = cleaned_data.get('end_hour')
        end_minute = cleaned_data.get('end_minute', 0) or 0
        
        # Obtener tiempo de descanso
        break_hours = cleaned_data.get('break_hours', 0) or 0
        break_minutes = cleaned_data.get('break_minutes', 0) or 0
        
        # Convertir horas y minutos a objetos Time
        if start_hour is not None:
            try:
                start_time = time_class(hour=start_hour, minute=start_minute)
                cleaned_data['start_time'] = start_time
            except ValueError:
                raise forms.ValidationError({'start_hour': 'Hora de inicio inválida.'})
        else:
            raise forms.ValidationError({'start_hour': 'La hora de inicio es requerida.'})
        
        if end_hour is not None:
            try:
                end_time = time_class(hour=end_hour, minute=end_minute)
                cleaned_data['end_time'] = end_time
            except ValueError:
                raise forms.ValidationError({'end_hour': 'Hora de fin inválida.'})
        else:
            raise forms.ValidationError({'end_hour': 'La hora de fin es requerida.'})
        
        # Convertir break_hours y break_minutes a total_break_time
        total_break_seconds = (break_hours * 3600) + (break_minutes * 60)
        cleaned_data['total_break_time'] = timedelta(seconds=total_break_seconds)
        
        # Validar que la fecha no sea futura
        if log_date and log_date > date.today():
            raise forms.ValidationError({'date': 'No puedes registrar trabajo para una fecha futura.'})
        
        # Validar que end_time sea después de start_time
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError({'end_hour': 'La hora de fin debe ser posterior a la hora de inicio.'})
        
        # Validar tiempo de descanso razonable
        if break_hours > 8:
            raise forms.ValidationError({'break_hours': 'El tiempo de descanso no puede ser mayor a 8 horas.'})
        
        # Validar que no exista otro registro para esta fecha (solo si no estamos editando)
        if log_date and self.employee:
            existing_log = DailyWorkLog.objects.filter(
                employee=self.employee,
                date=log_date
            ).first()
            
            # Si existe un registro y no es el que estamos editando
            if existing_log and (not self.instance or not self.instance.id or existing_log.id != self.instance.id):
                raise forms.ValidationError({
                    'date': f'Ya existe un registro de trabajo para la fecha {log_date.strftime("%d/%m/%Y")}. Por favor, edita el registro existente o elige otra fecha.'
                })
        
        return cleaned_data


@login_required
def create_work_log(request):
    """Vista para crear o actualizar registro de trabajo diario"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No se encontró perfil de empleado asociado a tu cuenta.')
        return redirect('employee_dashboard')
    
    # Obtener registro para hoy (si existe)
    today = date.today()
    work_log = DailyWorkLog.objects.filter(employee=employee, date=today).first()
    
    if request.method == 'POST':
        form = DailyWorkLogForm(request.POST, instance=work_log, employee=employee)
        if form.is_valid():
            # Obtener la fecha del formulario
            log_date = form.cleaned_data.get('date')
            
            # Verificar si ya existe un registro para esta fecha
            existing_log = DailyWorkLog.objects.filter(
                employee=employee, 
                date=log_date
            ).first()
            
            # Si existe un registro para esa fecha y NO es el que estamos editando
            if existing_log and (not work_log or existing_log.id != work_log.id):
                # Mostrar error claro al usuario
                form.add_error('date', f'Ya existe un registro para la fecha {log_date.strftime("%d/%m/%Y")}. Por favor, edita el registro existente o elige otra fecha.')
                messages.error(request, f'❌ Ya existe un registro de trabajo para la fecha {log_date.strftime("%d/%m/%Y")}. Por favor, elige otra fecha o edita el registro existente.')
            else:
                # Si no existe o es el mismo registro, guardar normalmente
                work_log = form.save(commit=False)
                work_log.employee = employee
                # Asignar start_time, end_time y total_break_time desde cleaned_data
                work_log.start_time = form.cleaned_data.get('start_time')
                work_log.end_time = form.cleaned_data.get('end_time')
                work_log.total_break_time = form.cleaned_data.get('total_break_time', timedelta(0))
                
                try:
                    work_log.save()
                    if existing_log:
                        messages.success(request, f'✅ Registro de trabajo actualizado correctamente para {log_date.strftime("%d/%m/%Y")}.')
                    else:
                        messages.success(request, f'✅ Registro de trabajo guardado correctamente para {log_date.strftime("%d/%m/%Y")}.')
                    return redirect('employee_dashboard')
                except Exception as e:
                    # Manejar errores de base de datos
                    import traceback
                    error_str = str(e)
                    if 'UNIQUE constraint' in error_str or 'unique' in error_str.lower():
                        messages.error(request, f'❌ Ya existe un registro de trabajo para la fecha {log_date.strftime("%d/%m/%Y")}. Este error no debería ocurrir. Por favor, intenta nuevamente o contacta al administrador.')
                        form.add_error('date', 'Ya existe un registro para esta fecha.')
                    else:
                        messages.error(request, f'❌ Error inesperado al guardar el registro. Por favor, intenta nuevamente.')
                        messages.error(request, f'Detalles técnicos: {error_str[:100]}')
                        # Log del error completo para debugging
                        print(f"Error completo: {traceback.format_exc()}")
        else:
            # Mostrar errores específicos del formulario
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            if error_messages:
                messages.error(request, '❌ Por favor, corrige los siguientes errores:')
                for msg in error_messages[:5]:  # Mostrar máximo 5 errores
                    messages.error(request, f'  • {msg}')
            else:
                messages.error(request, '❌ Por favor, corrige los errores en el formulario.')
    else:
        form = DailyWorkLogForm(instance=work_log, employee=employee)
    
    context = {
        'form': form,
        'work_log': work_log,
        'today': today,
    }
    
    return render(request, 'performance/create_work_log.html', context)


@login_required
def edit_work_log(request, log_id):
    """Vista para editar un registro de trabajo existente"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No se encontró perfil de empleado asociado a tu cuenta.')
        return redirect('employee_dashboard')
    
    work_log = get_object_or_404(DailyWorkLog, id=log_id, employee=employee)
    
    if request.method == 'POST':
        form = DailyWorkLogForm(request.POST, instance=work_log, employee=employee)
        if form.is_valid():
            work_log = form.save(commit=False)
            # Asignar start_time, end_time y total_break_time desde cleaned_data
            work_log.start_time = form.cleaned_data.get('start_time')
            work_log.end_time = form.cleaned_data.get('end_time')
            work_log.total_break_time = form.cleaned_data.get('total_break_time', timedelta(0))
            work_log.save()
            messages.success(request, '✅ Registro de trabajo actualizado correctamente.')
            return redirect('employee_dashboard')
        else:
            messages.error(request, '❌ Por favor, corrige los errores en el formulario.')
    else:
        form = DailyWorkLogForm(instance=work_log, employee=employee)
    
    context = {
        'form': form,
        'work_log': work_log,
    }
    
    return render(request, 'performance/create_work_log.html', context)

