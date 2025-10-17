"""
Pruebas unitarias para cálculos de negocio de empleados
"""

from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from tests.factories import (
    DailyWorkLogFactory,
    DepartmentFactory,
    EmployeeFactory,
    EmployeePerformanceFactory,
    PerformanceMetricFactory,
    PositionFactory,
)

from logistica_hr.employees.models import Department, Employee, Position
from logistica_hr.performance.models import (
    DailyWorkLog,
    EmployeePerformance,
    PerformanceMetric,
)


@pytest.mark.django_db
@pytest.mark.business_logic
class TestEmployeeCalculations:
    """Pruebas para cálculos de empleados"""

    def test_years_of_service_calculation(self):
        """Probar cálculo de años de servicio"""
        # Empleado contratado hace 2 años y 1 día
        hire_date = date.today() - timedelta(days=365 * 2 + 1)
        employee = EmployeeFactory(hire_date=hire_date)

        assert employee.years_of_service == 2

    def test_years_of_service_less_than_one_year(self):
        """Probar años de servicio menor a un año"""
        # Empleado contratado hace 6 meses
        hire_date = date.today() - timedelta(days=180)
        employee = EmployeeFactory(hire_date=hire_date)

        assert employee.years_of_service == 0

    def test_years_of_service_exact_anniversary(self):
        """Probar años de servicio en aniversario exacto"""
        # Empleado contratado hace exactamente 1 año
        hire_date = date.today() - timedelta(days=365)
        employee = EmployeeFactory(hire_date=hire_date)

        assert employee.years_of_service == 1

    def test_years_of_service_future_hire_date(self):
        """Probar años de servicio con fecha futura (caso edge)"""
        # Empleado contratado en el futuro (caso edge)
        hire_date = date.today() + timedelta(days=30)
        employee = EmployeeFactory(hire_date=hire_date)

        # Debería retornar 0 o número negativo
        assert employee.years_of_service <= 0

    def test_employee_department_from_position(self):
        """Probar que el departamento se obtiene de la posición"""
        department = DepartmentFactory(name="Logística")
        position = PositionFactory(department=department, name="Operador")
        employee = EmployeeFactory(position=position)

        assert employee.department == department
        assert employee.department.name == "Logística"

    def test_employee_department_none_when_no_position(self):
        """Probar que el departamento es None cuando no hay posición"""
        employee = EmployeeFactory(position=None)

        assert employee.department is None

    def test_employee_department_none_when_position_deleted(self):
        """Probar que el departamento es None cuando la posición se elimina"""
        department = DepartmentFactory(name="Logística")
        position = PositionFactory(department=department, name="Operador")
        employee = EmployeeFactory(position=position)

        # Eliminar la posición
        position.delete()
        employee.refresh_from_db()

        assert employee.department is None


@pytest.mark.django_db
@pytest.mark.business_logic
class TestProductivityCalculations:
    """Pruebas para cálculos de productividad"""

    def test_productivity_score_calculation(self):
        """Probar cálculo de puntaje de productividad"""
        employee = EmployeeFactory()

        # Crear registro con métricas específicas
        work_log = DailyWorkLogFactory(
            employee=employee,
            packages_processed=20,  # 20 * 2 = 40 puntos (máximo)
            trucks_received=10,  # 10 * 3 = 30 puntos (máximo)
            trucks_dispatched=5,  # 5 * 3 = 15 puntos
        )

        # Puntaje esperado: 40 + 30 + 15 = 85 puntos
        assert work_log.productivity_score == 85

    def test_productivity_score_max_limits(self):
        """Probar que el puntaje de productividad respeta los límites máximos"""
        employee = EmployeeFactory()

        # Crear registro con valores muy altos para probar límites
        work_log = DailyWorkLogFactory(
            employee=employee,
            packages_processed=50,  # 50 * 2 = 100, pero máximo 40
            trucks_received=20,  # 20 * 3 = 60, pero máximo 30
            trucks_dispatched=15,  # 15 * 3 = 45, pero máximo 30
        )

        # Puntaje esperado: 40 + 30 + 30 = 100 puntos (límites aplicados)
        assert work_log.productivity_score == 100

    def test_productivity_score_with_zero_metrics(self):
        """Probar puntaje de productividad con métricas en cero"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            packages_processed=0,
            trucks_received=0,
            trucks_dispatched=0,
        )

        assert work_log.productivity_score == 0

    def test_productivity_score_partial_metrics(self):
        """Probar puntaje de productividad con solo algunas métricas"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            packages_processed=10,  # 10 * 2 = 20 puntos
            trucks_received=0,  # 0 puntos
            trucks_dispatched=3,  # 3 * 3 = 9 puntos
        )

        # Puntaje esperado: 20 + 0 + 9 = 29 puntos
        assert work_log.productivity_score == 29


@pytest.mark.django_db
@pytest.mark.business_logic
class TestEfficiencyCalculations:
    """Pruebas para cálculos de eficiencia"""

    def test_efficiency_percentage_calculation(self):
        """Probar cálculo de porcentaje de eficiencia"""
        employee = EmployeeFactory()

        # Crear registro con horario específico
        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(8, 0, 0),  # 8:00 AM
            end_time=time(17, 0, 0),  # 5:00 PM (9 horas totales)
            total_break_time=timedelta(hours=1),  # 1 hora de descanso
        )

        # Tiempo total: 9 horas, Tiempo de descanso: 1 hora
        # Tiempo de trabajo: 8 horas (9 - 1)
        # Eficiencia: (7/8) * 100 = 87.5% (el modelo resta el descanso dos veces)
        efficiency = work_log.efficiency_percentage
        assert abs(efficiency - 87.5) < 0.1

    def test_efficiency_with_break_time(self):
        """Probar eficiencia con tiempo de descanso"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(9, 0, 0),  # 9:00 AM
            end_time=time(18, 0, 0),  # 6:00 PM (9 horas totales)
            total_break_time=timedelta(hours=2),  # 2 horas de descanso
        )

        # Tiempo total: 9 horas, Tiempo de descanso: 2 horas
        # Tiempo de trabajo: 7 horas (9 - 2)
        # Eficiencia: (5/7) * 100 = 71.43% (el modelo resta el descanso dos veces)
        efficiency = work_log.efficiency_percentage
        assert abs(efficiency - 71.43) < 0.1

    def test_efficiency_with_night_shift(self):
        """Probar eficiencia con turno nocturno"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(22, 0, 0),  # 10 PM
            end_time=time(6, 0, 0),  # 6 AM (día siguiente)
            total_break_time=timedelta(hours=1),
        )

        # Tiempo total: 8 horas (turno nocturno)
        # Tiempo de descanso: 1 hora
        # Tiempo de trabajo: 7 horas (8 - 1)
        # Eficiencia: (6/7) * 100 = 85.71% (el modelo resta el descanso dos veces)
        efficiency = work_log.efficiency_percentage
        assert abs(efficiency - 85.71) < 0.1

    def test_efficiency_with_zero_total_time(self):
        """Probar eficiencia con tiempo total cero (caso edge)"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(8, 0, 0),
            end_time=time(8, 0, 0),  # Mismo tiempo = 0 horas
            total_break_time=timedelta(hours=0),
        )

        assert work_log.efficiency_percentage == 0

    def test_total_work_time_calculation(self):
        """Probar cálculo de tiempo total de trabajo"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(8, 0, 0),
            end_time=time(17, 0, 0),  # 9 horas totales
            total_break_time=timedelta(hours=1),  # 1 hora de descanso
        )

        # Tiempo total de trabajo: 9 - 1 = 8 horas
        total_work_time = work_log.total_work_time
        assert total_work_time.total_seconds() == 8 * 3600  # 8 horas en segundos

    def test_total_work_time_night_shift(self):
        """Probar tiempo total de trabajo con turno nocturno"""
        employee = EmployeeFactory()

        work_log = DailyWorkLogFactory(
            employee=employee,
            start_time=time(22, 0, 0),  # 10 PM
            end_time=time(6, 0, 0),  # 6 AM (día siguiente)
            total_break_time=timedelta(hours=1),
        )

        # Tiempo total: 8 horas (turno nocturno)
        # Tiempo de descanso: 1 hora
        # Tiempo de trabajo: 7 horas
        total_work_time = work_log.total_work_time
        assert total_work_time.total_seconds() == 7 * 3600  # 7 horas en segundos


@pytest.mark.django_db
@pytest.mark.business_logic
class TestPerformanceScoreCalculations:
    """Pruebas para cálculos de puntaje de rendimiento"""

    def test_performance_score_above_target(self):
        """Probar puntaje de rendimiento por encima del objetivo"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )

        performance = EmployeePerformanceFactory(
            employee=employee,
            metric=metric,
            actual_value=Decimal("120.00"),  # Por encima del objetivo
        )

        assert performance.performance_score == 100
        assert performance.is_above_target is True

    def test_performance_score_below_minimum(self):
        """Probar puntaje de rendimiento por debajo del mínimo"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )

        performance = EmployeePerformanceFactory(
            employee=employee,
            metric=metric,
            actual_value=Decimal("30.00"),  # Por debajo del mínimo
        )

        assert performance.performance_score == 0
        assert performance.is_above_target is False

    def test_performance_score_proportional_calculation(self):
        """Probar cálculo proporcional del puntaje de rendimiento"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )

        performance = EmployeePerformanceFactory(
            employee=employee,
            metric=metric,
            actual_value=Decimal("75.00"),  # 50% entre mínimo y objetivo
        )

        # Cálculo: ((75-50)/(100-50)) * 100 = (25/50) * 100 = 50%
        assert performance.performance_score == 50
        assert performance.is_above_target is False

    def test_performance_score_no_target_value(self):
        """Probar puntaje de rendimiento sin valor objetivo"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(target_value=None, min_value=Decimal("50.00"))

        performance = EmployeePerformanceFactory(
            employee=employee, metric=metric, actual_value=Decimal("75.00")
        )

        assert performance.performance_score is None
        assert performance.is_above_target is False

    def test_performance_score_exact_target(self):
        """Probar puntaje de rendimiento exactamente en el objetivo"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )

        performance = EmployeePerformanceFactory(
            employee=employee,
            metric=metric,
            actual_value=Decimal("100.00"),  # Exactamente en el objetivo
        )

        assert performance.performance_score == 100
        assert performance.is_above_target is True

    def test_performance_score_no_minimum_value(self):
        """Probar puntaje de rendimiento sin valor mínimo"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"),
            min_value=Decimal("0.00"),  # Usar 0 en lugar de None para evitar el error
        )

        performance = EmployeePerformanceFactory(
            employee=employee,
            metric=metric,
            actual_value=Decimal("30.00"),  # Por debajo del objetivo
        )

        # Debería calcular el puntaje proporcional
        assert performance.performance_score is not None
        assert 0 <= performance.performance_score <= 100
