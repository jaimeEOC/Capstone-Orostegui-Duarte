"""
Pruebas unitarias para el modelo WorkSchedule
"""

import pytest
from datetime import time, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from logistica_hr.employees.models import WorkSchedule
from tests.factories import WorkScheduleFactory, EmployeeFactory


@pytest.mark.django_db
@pytest.mark.models
class TestWorkSchedule:
    """Pruebas para el modelo WorkSchedule"""

    def test_work_schedule_creation(self):
        """Probar creación básica de horario de trabajo"""
        schedule = WorkScheduleFactory()
        assert schedule.pk is not None
        assert schedule.employee is not None
        assert schedule.day_of_week is not None
        assert schedule.start_time is not None
        assert schedule.end_time is not None

    def test_work_schedule_str_representation(self):
        """Probar representación string del horario"""
        employee = EmployeeFactory()
        schedule = WorkScheduleFactory(employee=employee, day_of_week=0)
        expected = f"{employee} - Lunes"
        assert str(schedule) == expected

    def test_work_schedule_day_of_week_choices(self):
        """Probar opciones válidas de día de la semana"""
        valid_days = [0, 1, 2, 3, 4, 5, 6]  # Lunes a Domingo

        for day in valid_days:
            schedule = WorkScheduleFactory(day_of_week=day)
            assert schedule.day_of_week == day
            assert schedule.get_day_of_week_display() is not None

    def test_work_schedule_break_times_optional(self):
        """Probar que break_start y break_end son opcionales"""
        schedule = WorkScheduleFactory(break_start=None, break_end=None)
        assert schedule.break_start is None
        assert schedule.break_end is None

    def test_work_schedule_ordering(self):
        """Probar ordenamiento por empleado y día de la semana"""
        employee1 = EmployeeFactory()
        employee2 = EmployeeFactory()

        schedule1 = WorkScheduleFactory(employee=employee1, day_of_week=2)
        schedule2 = WorkScheduleFactory(employee=employee1, day_of_week=0)
        schedule3 = WorkScheduleFactory(employee=employee2, day_of_week=1)

        schedules = WorkSchedule.objects.all()
        # Deberían estar ordenados por employee, luego day_of_week
        assert schedules[0].employee == employee1
        assert schedules[0].day_of_week == 0
        assert schedules[1].employee == employee1
        assert schedules[1].day_of_week == 2
        assert schedules[2].employee == employee2


@pytest.mark.django_db
@pytest.mark.models
class TestWorkScheduleUniqueTogether:
    """Pruebas de unicidad de WorkSchedule"""

    def test_work_schedule_unique_together(self):
        """Probar unicidad de (employee, day_of_week)"""
        employee = EmployeeFactory()
        day = 0  # Lunes

        WorkScheduleFactory(employee=employee, day_of_week=day)

        with pytest.raises(IntegrityError):
            WorkScheduleFactory(employee=employee, day_of_week=day)

    def test_work_schedule_different_employee_same_day(self):
        """Probar que diferentes empleados pueden tener horario el mismo día"""
        day = 0  # Lunes

        schedule1 = WorkScheduleFactory(day_of_week=day)
        schedule2 = WorkScheduleFactory(day_of_week=day)

        assert schedule1.employee != schedule2.employee
        assert schedule1.day_of_week == schedule2.day_of_week

    def test_work_schedule_same_employee_different_days(self):
        """Probar que mismo empleado puede tener horarios en diferentes días"""
        employee = EmployeeFactory()

        schedule1 = WorkScheduleFactory(employee=employee, day_of_week=0)
        schedule2 = WorkScheduleFactory(employee=employee, day_of_week=1)
        schedule3 = WorkScheduleFactory(employee=employee, day_of_week=2)

        assert schedule1.employee == schedule2.employee == schedule3.employee
        assert schedule1.day_of_week != schedule2.day_of_week
        assert schedule2.day_of_week != schedule3.day_of_week


@pytest.mark.django_db
@pytest.mark.models
class TestWorkScheduleCalculations:
    """Pruebas para cálculos de WorkSchedule"""

    def test_total_hours_basic(self):
        """Probar cálculo básico de horas totales"""
        schedule = WorkScheduleFactory(
            start_time=time(9, 0),  # 9:00 AM
            end_time=time(17, 0),  # 5:00 PM
        )

        # 17:00 - 9:00 = 8 horas
        assert schedule.total_hours == 8.0

    def test_total_hours_with_minutes(self):
        """Probar cálculo de horas con minutos"""
        schedule = WorkScheduleFactory(
            start_time=time(8, 30),  # 8:30 AM
            end_time=time(16, 45),  # 4:45 PM
        )

        # 16:45 - 8:30 = 8 horas y 15 minutos = 8.25 horas
        assert abs(schedule.total_hours - 8.25) < 0.01

    def test_total_hours_crosses_midnight(self):
        """Probar cálculo cuando el horario cruza medianoche"""
        schedule = WorkScheduleFactory(
            start_time=time(22, 0),  # 10:00 PM
            end_time=time(6, 0),  # 6:00 AM siguiente día
        )

        # 24:00 - 22:00 + 6:00 = 8 horas
        assert schedule.total_hours == 8.0

    def test_total_hours_exact_hours(self):
        """Probar cálculo de horas exactas"""
        schedule = WorkScheduleFactory(
            start_time=time(9, 0),
            end_time=time(18, 0),
        )

        # 18:00 - 9:00 = 9 horas
        assert schedule.total_hours == 9.0

    def test_total_hours_partial_hour(self):
        """Probar cálculo de menos de una hora"""
        schedule = WorkScheduleFactory(
            start_time=time(9, 0),
            end_time=time(9, 30),
        )

        # 9:30 - 9:00 = 0.5 horas
        assert schedule.total_hours == 0.5

    def test_total_hours_overnight_shift(self):
        """Probar cálculo de turno nocturno completo"""
        schedule = WorkScheduleFactory(
            start_time=time(23, 0),  # 11:00 PM
            end_time=time(7, 0),  # 7:00 AM siguiente día
        )

        # 24:00 - 23:00 + 7:00 = 8 horas
        assert schedule.total_hours == 8.0


@pytest.mark.django_db
@pytest.mark.models
class TestWorkScheduleRelationships:
    """Pruebas de relaciones de WorkSchedule"""

    def test_work_schedule_employee_relationship(self):
        """Probar relación con Employee"""
        employee = EmployeeFactory()
        schedule1 = WorkScheduleFactory(employee=employee, day_of_week=0)
        schedule2 = WorkScheduleFactory(employee=employee, day_of_week=1)

        assert schedule1.employee == employee
        assert schedule2.employee == employee
        assert schedule1 in employee.work_schedules.all()
        assert schedule2 in employee.work_schedules.all()

    def test_work_schedule_employee_cascade_delete(self):
        """Probar que al eliminar Employee se eliminan los horarios"""
        employee = EmployeeFactory()
        schedule1 = WorkScheduleFactory(employee=employee, day_of_week=0)
        schedule2 = WorkScheduleFactory(employee=employee, day_of_week=1)

        employee.delete()

        assert not WorkSchedule.objects.filter(pk=schedule1.pk).exists()
        assert not WorkSchedule.objects.filter(pk=schedule2.pk).exists()


@pytest.mark.django_db
@pytest.mark.models
class TestWorkScheduleBreakTimes:
    """Pruebas para tiempos de descanso"""

    def test_work_schedule_with_break_times(self):
        """Probar horario con tiempos de descanso"""
        schedule = WorkScheduleFactory(
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_start=time(13, 0),  # 1:00 PM
            break_end=time(14, 0),  # 2:00 PM
        )

        assert schedule.break_start == time(13, 0)
        assert schedule.break_end == time(14, 0)

    def test_work_schedule_break_start_without_end(self):
        """Probar que break_start puede existir sin break_end"""
        schedule = WorkScheduleFactory(
            break_start=time(13, 0),
            break_end=None,
        )

        assert schedule.break_start == time(13, 0)
        assert schedule.break_end is None

    def test_work_schedule_break_end_without_start(self):
        """Probar que break_end puede existir sin break_start"""
        schedule = WorkScheduleFactory(
            break_start=None,
            break_end=time(14, 0),
        )

        assert schedule.break_start is None
        assert schedule.break_end == time(14, 0)


@pytest.mark.django_db
@pytest.mark.models
class TestWorkScheduleMultipleDays:
    """Pruebas para múltiples días de horario"""

    def test_employee_full_week_schedule(self):
        """Probar que un empleado puede tener horario para toda la semana"""
        employee = EmployeeFactory()

        for day in range(7):  # Lunes a Domingo
            WorkScheduleFactory(employee=employee, day_of_week=day)

        schedules = employee.work_schedules.all()
        assert schedules.count() == 7

        # Verificar que todos los días están presentes
        days = set(schedules.values_list("day_of_week", flat=True))
        assert days == {0, 1, 2, 3, 4, 5, 6}

    def test_employee_partial_week_schedule(self):
        """Probar que un empleado puede tener horario solo algunos días"""
        employee = EmployeeFactory()

        # Solo lunes, miércoles y viernes
        WorkScheduleFactory(employee=employee, day_of_week=0)
        WorkScheduleFactory(employee=employee, day_of_week=2)
        WorkScheduleFactory(employee=employee, day_of_week=4)

        schedules = employee.work_schedules.all()
        assert schedules.count() == 3

        days = set(schedules.values_list("day_of_week", flat=True))
        assert days == {0, 2, 4}

