from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import TaskCategory, Task, TaskTimeLog, TaskComment
from logistica_hr.users.models import User
# OJO: NO registramos Employee aquí para evitar errores de campos inexistentes en autocomplete

# ---------- Admin mínimo para User (requerido por TaskAdmin.autocomplete_fields) ----------
try:
    @admin.register(User)
    class UserAdmin(admin.ModelAdmin):
        list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff')
        search_fields = ('username', 'first_name', 'last_name', 'email', 'role')
        list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
except AlreadyRegistered:
    pass

# ---------------- Admin de tus modelos de tasks ----------------
@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'color')
    search_fields = ('name',)
    ordering = ('priority', 'name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_by', 'assigned_to', 'status', 'priority', 'due_date', 'template')
    list_filter  = ('status', 'priority', 'template', 'category')
    search_fields = ('title', 'description', 'notes')
    date_hierarchy = 'due_date'

    # 👇 Evitamos exigir admin para Employee usando raw_id_fields
    raw_id_fields = ('assigned_to',)

    # 👇 Mantenemos autocomplete donde sí tenemos admin con search_fields
    autocomplete_fields = ('assigned_by', 'category')

@admin.register(TaskTimeLog)
class TaskTimeLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'employee', 'start_time', 'end_time', 'is_break')
    list_filter = ('is_break',)
    search_fields = ('task__title', 'employee__user__username')

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at', 'is_internal')
    list_filter = ('is_internal',)
    search_fields = ('task__title', 'author__username', 'content')
