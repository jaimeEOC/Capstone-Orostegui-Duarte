"""
Vistas para la aplicación employees
"""
# DRF
from rest_framework import viewsets, permissions, filters

from .models import Department, Position, Employee, WorkSchedule

# === DRF Serializers (usa los tuyos si ya existen) ===========================
# Si YA tienes serializers.py, descomenta estas dos líneas e importa desde ahí:
# from .serializers import (
#     DepartmentSerializer, PositionSerializer, EmployeeSerializer, WorkScheduleSerializer
# )

# Si NO tienes serializers aún, puedes usar estos mínimos integrados:
try:
    from .serializers import (
        DepartmentSerializer, PositionSerializer, EmployeeSerializer, WorkScheduleSerializer
    )
except Exception:
    from rest_framework import serializers

    class DepartmentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Department
            fields = "__all__"

    class PositionSerializer(serializers.ModelSerializer):
        class Meta:
            model = Position
            fields = "__all__"

    class EmployeeSerializer(serializers.ModelSerializer):
        full_name = serializers.SerializerMethodField()

        class Meta:
            model = Employee
            fields = "__all__"

        def get_full_name(self, obj):
            return obj.user.get_full_name() if getattr(obj, "user", None) else ""

    class WorkScheduleSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkSchedule
            fields = "__all__"


# === DRF ViewSets básicos =====================================================
class DefaultAuthPermission(permissions.IsAuthenticated):
    """Atajo por si quieres cambiar política de permisos global aquí."""
    pass


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    CRUD de Departamentos
    """
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [DefaultAuthPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]


class PositionViewSet(viewsets.ModelViewSet):
    """
    CRUD de Cargos/Posiciones
    """
    queryset = (
        Position.objects
        .select_related("department")
        .all()
        .order_by("name")
    )
    serializer_class = PositionSerializer
    permission_classes = [DefaultAuthPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "department__name"]
    ordering_fields = ["name", "department", "created_at", "updated_at"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD de Empleados
    """
    queryset = (
        Employee.objects
        .select_related("user", "position", "position__department", "supervisor__user")
        .prefetch_related("skills", "work_schedules")  # ajusta según tus M2M/relaciones
        .all()
        .order_by("user__first_name", "user__last_name", "employee_id")
    )
    serializer_class = EmployeeSerializer
    permission_classes = [DefaultAuthPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__first_name", "user__last_name", "user__email",
        "employee_id", "position__name", "position__department__name"
    ]
    ordering_fields = [
        "employee_id", "hire_date", "is_active",
        "position__name", "position__department__name", "created_at", "updated_at"
    ]


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD de Horarios de Trabajo
    """
    queryset = (
        WorkSchedule.objects
        .select_related("employee", "employee__user")
        .all()
        .order_by("-start_time")
    )
    serializer_class = WorkScheduleSerializer
    permission_classes = [DefaultAuthPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "employee__user__first_name", "employee__user__last_name", "employee__employee_id"
    ]
    ordering_fields = ["start_time", "end_time", "created_at", "updated_at"]
