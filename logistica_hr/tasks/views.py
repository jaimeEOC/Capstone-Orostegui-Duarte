from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from logistica_hr.tasks.models import Task
from logistica_hr.employees.models import Employee


def _fmt(dt):
    if not dt:
        return None
    tz = timezone.get_current_timezone()
    return timezone.localtime(dt, tz).strftime("%d/%m/%Y %H:%M")


@ensure_csrf_cookie
@login_required
def my_tasks(request):
    base = Task.objects.select_related('assigned_to', 'assigned_to__user', 'category')
    emp = Employee.objects.filter(user=request.user).first()
    qs = base.filter(assigned_to=emp) if emp else base.filter(assigned_to__user_id=request.user.id)
    qs = qs.order_by('-assigned_at', '-due_date', 'priority')
    return render(request, 'tasks/my_tasks.html', {'my_tasks': qs})


@login_required
@require_POST
def update_task_status_api(request, task_id, new_status):
    """
    new_status ∈ {"in_progress", "completed"}
    """
    task = get_object_or_404(
        Task.objects.select_related('assigned_to__user'),
        id=task_id
    )

    # Seguridad: solo el asignado puede cambiar su tarea
    if not task.assigned_to or task.assigned_to.user_id != request.user.id:
        return HttpResponseForbidden("No autorizado")

    if new_status not in ("in_progress", "completed"):
        return JsonResponse({"ok": False, "error": "Estado inválido"}, status=400)

    # Timestamps y cambio de estado
    if new_status == "in_progress" and not task.start_date:
        task.start_date = timezone.now()
    if new_status == "completed":
        task.completion_date = timezone.now()

    task.status = new_status

    # Guarda solo campos existentes
    fields = ['status']
    if 'start_date' in task.__dict__:
        fields.append('start_date')
    if 'completion_date' in task.__dict__:
        fields.append('completion_date')
    if 'updated_at' in task.__dict__:
        task.updated_at = timezone.now()
        fields.append('updated_at')

    task.save(update_fields=fields)

    return JsonResponse({
        "ok": True,
        "task_id": task.id,
        "status": task.status,
        "started_at": _fmt(getattr(task, 'start_date', None)),
        "completed_at": _fmt(getattr(task, 'completion_date', None)),
    })


# === Crear tarea (sin categoría) ===

class TaskMiniForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        input_formats=[
            '%Y-%m-%dT%H:%M',  # 2025-10-07T17:34  (datetime-local)
            '%Y-%m-%d %H:%M',  # 2025-10-07 17:34
            '%d-%m-%Y %H:%M',  # 07-10-2025 17:34  👈 tu formato
            '%d/%m/%Y %H:%M',  # 07/10/2025 17:34
        ],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        required=True,
        label='Fecha de vencimiento'
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "priority", "due_date", "estimated_hours", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Título", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Descripción", "class": "form-control"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "estimated_hours": forms.NumberInput(attrs={"class": "form-control", "step": "0.25", "min": "0"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = Employee.objects.select_related("user").order_by("user__username")
        self.fields["assigned_to"].label = "Asignar a empleado"
        self.fields["estimated_hours"].required = False
        if "status" in self.fields and not self.initial.get("status"):
            self.fields["status"].initial = "pending"


# views.py
@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskMiniForm(request.POST)
        # 👇 Esto es la clave: setear antes de is_valid()
        form.instance.assigned_by = request.user

        if form.is_valid():
            task = form.save(commit=False)
            # ya viene con assigned_by
            if not getattr(task, "status", None):
                task.status = "pending"
            task.save()
            messages.success(request, "✅ Tarea creada correctamente.")
            return redirect('supervisor_dashboard')
        else:
            messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = TaskMiniForm()

    return render(request, 'tasks/create_task.html', {'form': form})

