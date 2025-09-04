"""
Vistas básicas para la aplicación employees
"""

from rest_framework import viewsets
from .models import Department, Position, Employee, WorkSchedule

# ViewSets básicos (se implementarán después)
class DepartmentViewSet(viewsets.ModelViewSet):
    pass

class PositionViewSet(viewsets.ModelViewSet):
    pass

class EmployeeViewSet(viewsets.ModelViewSet):
    pass

class WorkScheduleViewSet(viewsets.ModelViewSet):
    pass


