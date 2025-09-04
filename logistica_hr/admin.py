"""
Configuración del admin de Django para el proyecto Logistica HR
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from logistica_hr.users.models import User
from logistica_hr.employees.models import Department, Position, Employee, WorkSchedule
from logistica_hr.tasks.models import TaskCategory, Task, TaskTimeLog, TaskComment
from logistica_hr.performance.models import (
    PerformanceMetric, EmployeePerformance, DailyWorkLog, PerformanceEvaluation
)
from logistica_hr.reports.models import (
    ReportTemplate, ScheduledReport, GeneratedReport, ReportParameter
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo User
    """
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role',
        'department', 'is_active', 'date_joined'
    ]
    list_filter = ['role', 'department', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'employee_id']
    ordering = ['username']
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Información Adicional'), {
            'fields': ('role', 'phone', 'department', 'employee_id')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Información Adicional'), {
            'fields': ('role', 'phone', 'department', 'employee_id')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Department
    """
    list_display = ['name', 'manager', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Position
    """
    list_display = ['name', 'department', 'base_salary', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['department', 'name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Employee
    """
    list_display = [
        'employee_id', 'user', 'position', 'supervisor',
        'hire_date', 'is_active'
    ]
    list_filter = ['position__department', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name']
    ordering = ['employee_id']
    raw_id_fields = ['user', 'position', 'supervisor']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    """
    Admin para el modelo WorkSchedule
    """
    list_display = ['employee', 'day_of_week', 'start_time', 'end_time', 'total_hours']
    list_filter = ['day_of_week', 'employee__position__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering = ['employee', 'day_of_week']


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    """
    Admin para el modelo TaskCategory
    """
    list_display = ['name', 'metric_type', 'priority', 'color', 'is_active']
    list_filter = ['metric_type', 'priority', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['priority', 'name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Task
    """
    list_display = [
        'title', 'assigned_to', 'status', 'priority', 'due_date',
        'estimated_hours', 'actual_hours', 'is_overdue'
    ]
    list_filter = ['status', 'priority', 'category', 'assigned_to__position__department']
    search_fields = ['title', 'description', 'assigned_to__user__first_name']
    ordering = ['-due_date', 'priority']
    raw_id_fields = ['assigned_to', 'assigned_by']
    readonly_fields = ['start_date', 'completion_date', 'is_overdue']


@admin.register(TaskTimeLog)
class TaskTimeLogAdmin(admin.ModelAdmin):
    """
    Admin para el modelo TaskTimeLog
    """
    list_display = ['task', 'employee', 'start_time', 'end_time', 'duration_hours', 'is_break']
    list_filter = ['is_break', 'start_time__date', 'employee__position__department']
    search_fields = ['task__title', 'employee__user__first_name']
    ordering = ['-start_time']
    raw_id_fields = ['task', 'employee']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """
    Admin para el modelo TaskComment
    """
    list_display = ['task', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['task__title', 'author__username', 'content']
    ordering = ['-created_at']
    raw_id_fields = ['task', 'author']


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """
    Admin para el modelo PerformanceMetric
    """
    list_display = ['name', 'metric_type', 'unit', 'target_value', 'weight', 'is_active']
    list_filter = ['metric_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['metric_type', 'name']


@admin.register(EmployeePerformance)
class EmployeePerformanceAdmin(admin.ModelAdmin):
    """
    Admin para el modelo EmployeePerformance
    """
    list_display = [
        'employee', 'metric', 'date', 'actual_value',
        'performance_score', 'is_above_target'
    ]
    list_filter = ['metric__metric_type', 'date', 'employee__position__department']
    search_fields = ['employee__user__first_name', 'metric__name']
    ordering = ['-date', 'employee']
    raw_id_fields = ['employee', 'metric', 'evaluated_by']
    readonly_fields = ['performance_score', 'is_above_target']


@admin.register(DailyWorkLog)
class DailyWorkLogAdmin(admin.ModelAdmin):
    """
    Admin para el modelo DailyWorkLog
    """
    list_display = [
        'employee', 'date', 'start_time', 'end_time',
        'packages_processed', 'trucks_received', 'productivity_score'
    ]
    list_filter = ['date', 'employee__position__department']
    search_fields = ['employee__user__first_name', 'notes']
    ordering = ['-date', 'employee']
    raw_id_fields = ['employee']
    readonly_fields = ['total_work_time', 'productivity_score', 'efficiency_percentage']


@admin.register(PerformanceEvaluation)
class PerformanceEvaluationAdmin(admin.ModelAdmin):
    """
    Admin para el modelo PerformanceEvaluation
    """
    list_display = [
        'employee', 'evaluation_type', 'start_date', 'end_date',
        'overall_score', 'evaluated_by'
    ]
    list_filter = ['evaluation_type', 'start_date', 'end_date']
    search_fields = ['employee__user__first_name', 'strengths', 'areas_for_improvement']
    ordering = ['-end_date', 'employee']
    raw_id_fields = ['employee', 'evaluated_by']
    readonly_fields = ['duration_days']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """
    Admin para el modelo ReportTemplate
    """
    list_display = ['name', 'report_type', 'format', 'is_active']
    list_filter = ['report_type', 'format', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['report_type', 'name']


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    """
    Admin para el modelo ScheduledReport
    """
    list_display = ['name', 'template', 'frequency', 'next_generation', 'is_active']
    list_filter = ['frequency', 'is_active', 'template__report_type']
    search_fields = ['name', 'template__name']
    ordering = ['-next_generation']
    raw_id_fields = ['template']


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """
    Admin para el modelo GeneratedReport
    """
    list_display = [
        'name', 'template', 'status', 'generated_by',
        'file_size_mb', 'created_at'
    ]
    list_filter = ['status', 'template__report_type', 'created_at']
    search_fields = ['name', 'template__name']
    ordering = ['-created_at']
    raw_id_fields = ['template', 'scheduled_report', 'generated_by']
    readonly_fields = ['file_size_mb', 'is_successful']


@admin.register(ReportParameter)
class ReportParameterAdmin(admin.ModelAdmin):
    """
    Admin para el modelo ReportParameter
    """
    list_display = ['name', 'display_name', 'parameter_type', 'is_required']
    list_filter = ['parameter_type', 'is_required']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['name']


# Configuración del sitio admin
admin.site.site_header = _('Administración de Logistica HR')
admin.site.site_title = _('Logistica HR Admin')
admin.site.index_title = _('Panel de Control de Logistica HR')


