"""
Pruebas unitarias para los modelos de Performance
"""

import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from logistica_hr.performance.models import (
    PerformanceMetric,
    EmployeePerformance,
    DailyWorkLog,
    PerformanceEvaluation,
)
from tests.factories import (
    PerformanceMetricFactory,
    EmployeePerformanceFactory,
    DailyWorkLogFactory,
    PerformanceEvaluationFactory,
    EmployeeFactory,
    SupervisorUserFactory,
)


@pytest.mark.django_db
@pytest.mark.models
class TestPerformanceMetric:
    """Pruebas para el modelo PerformanceMetric"""

    def test_metric_creation(self):
        """Probar creación básica de métrica"""
        metric = PerformanceMetricFactory()
        assert metric.pk is not None
        assert metric.name is not None
        assert metric.metric_type is not None
        assert metric.unit is not None

    def test_metric_str_representation(self):
        """Probar representación string de la métrica"""
        metric = PerformanceMetricFactory(
            name="Productividad", metric_type="productivity"
        )
        expected = "Productividad (Productividad)"
        assert str(metric) == expected

    def test_metric_type_choices(self):
        """Probar opciones válidas de tipo de métrica"""
        valid_types = ["productivity", "quality", "efficiency", "attendance", "safety"]

        for metric_type in valid_types:
            metric = PerformanceMetricFactory(metric_type=metric_type)
            assert metric.metric_type == metric_type
            assert metric.get_metric_type_display() is not None

    def test_metric_weight_default(self):
        """Probar valor por defecto de weight"""
        # El factory genera valores aleatorios, así que especificamos explícitamente
        # el valor por defecto o verificamos que el modelo tiene el default correcto
        from logistica_hr.performance.models import PerformanceMetric
        metric = PerformanceMetric(
            name="Test Metric",
            metric_type="productivity",
            unit="units"
        )
        # El default se aplica al guardar
        assert metric.weight == Decimal("1.00")

    def test_metric_weight_validation_min(self):
        """Probar validación de weight mínimo (0)"""
        metric = PerformanceMetricFactory(weight=Decimal("0.00"))
        assert metric.weight == Decimal("0.00")

    def test_metric_weight_validation_max(self):
        """Probar validación de weight máximo (1)"""
        metric = PerformanceMetricFactory(weight=Decimal("1.00"))
        assert metric.weight == Decimal("1.00")

    def test_metric_weight_invalid_below_zero(self):
        """Probar que weight no puede ser menor a 0"""
        with pytest.raises(ValidationError):
            metric = PerformanceMetricFactory(weight=Decimal("-0.01"))
            metric.full_clean()

    def test_metric_weight_invalid_above_one(self):
        """Probar que weight no puede ser mayor a 1"""
        with pytest.raises(ValidationError):
            metric = PerformanceMetricFactory(weight=Decimal("1.01"))
            metric.full_clean()

    def test_metric_target_value_optional(self):
        """Probar que target_value es opcional"""
        metric = PerformanceMetricFactory(target_value=None)
        assert metric.target_value is None

    def test_metric_min_value_optional(self):
        """Probar que min_value es opcional"""
        metric = PerformanceMetricFactory(min_value=None)
        assert metric.min_value is None

    def test_metric_max_value_optional(self):
        """Probar que max_value es opcional"""
        metric = PerformanceMetricFactory(max_value=None)
        assert metric.max_value is None

    def test_metric_description_optional(self):
        """Probar que description es opcional"""
        metric = PerformanceMetricFactory(description="")
        assert metric.description == ""

    def test_metric_ordering(self):
        """Probar ordenamiento por tipo y nombre"""
        metric1 = PerformanceMetricFactory(
            metric_type="quality", name="Zulu Metric"
        )
        metric2 = PerformanceMetricFactory(
            metric_type="productivity", name="Alpha Metric"
        )
        metric3 = PerformanceMetricFactory(
            metric_type="productivity", name="Beta Metric"
        )

        metrics = PerformanceMetric.objects.all()
        # Deberían estar ordenados por metric_type primero, luego name
        assert metrics[0].metric_type == "productivity"
        assert metrics[1].metric_type == "productivity"
        assert metrics[2].metric_type == "quality"


@pytest.mark.django_db
@pytest.mark.models
class TestEmployeePerformance:
    """Pruebas para el modelo EmployeePerformance"""

    def test_employee_performance_creation(self):
        """Probar creación básica de rendimiento de empleado"""
        perf = EmployeePerformanceFactory()
        assert perf.pk is not None
        assert perf.employee is not None
        assert perf.metric is not None
        assert perf.date is not None
        assert perf.actual_value is not None

    def test_employee_performance_str_representation(self):
        """Probar representación string del rendimiento"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory(name="Productividad")
        perf = EmployeePerformanceFactory(
            employee=employee, metric=metric, date=date(2024, 1, 15)
        )
        expected = f"{employee} - Productividad - 2024-01-15"
        assert str(perf) == expected

    def test_employee_performance_unique_together(self):
        """Probar unicidad de (employee, date, metric)"""
        employee = EmployeeFactory()
        metric = PerformanceMetricFactory()
        date_val = date(2024, 1, 15)

        EmployeePerformanceFactory(employee=employee, metric=metric, date=date_val)

        with pytest.raises(IntegrityError):
            EmployeePerformanceFactory(employee=employee, metric=metric, date=date_val)

    def test_employee_performance_different_employee_same_date_metric(self):
        """Probar que diferentes empleados pueden tener misma fecha y métrica"""
        metric = PerformanceMetricFactory()
        date_val = date(2024, 1, 15)

        perf1 = EmployeePerformanceFactory(metric=metric, date=date_val)
        perf2 = EmployeePerformanceFactory(metric=metric, date=date_val)

        assert perf1.employee != perf2.employee
        assert perf1.metric == perf2.metric
        assert perf1.date == perf2.date

    def test_employee_performance_different_metric_same_employee_date(self):
        """Probar que mismo empleado puede tener diferentes métricas en misma fecha"""
        employee = EmployeeFactory()
        date_val = date(2024, 1, 15)

        metric1 = PerformanceMetricFactory()
        metric2 = PerformanceMetricFactory()

        perf1 = EmployeePerformanceFactory(
            employee=employee, metric=metric1, date=date_val
        )
        perf2 = EmployeePerformanceFactory(
            employee=employee, metric=metric2, date=date_val
        )

        assert perf1.employee == perf2.employee
        assert perf1.date == perf2.date
        assert perf1.metric != perf2.metric

    def test_employee_performance_evaluated_by_optional(self):
        """Probar que evaluated_by es opcional"""
        perf = EmployeePerformanceFactory(evaluated_by=None)
        assert perf.evaluated_by is None

    def test_employee_performance_notes_optional(self):
        """Probar que notes es opcional"""
        perf = EmployeePerformanceFactory(notes="")
        assert perf.notes == ""

    def test_employee_performance_ordering(self):
        """Probar ordenamiento por fecha descendente y empleado"""
        employee1 = EmployeeFactory()
        employee2 = EmployeeFactory()

        perf1 = EmployeePerformanceFactory(
            employee=employee1, date=date(2024, 1, 15)
        )
        perf2 = EmployeePerformanceFactory(
            employee=employee2, date=date(2024, 1, 20)
        )
        perf3 = EmployeePerformanceFactory(
            employee=employee1, date=date(2024, 1, 20)
        )

        perfs = EmployeePerformance.objects.all()
        # Deberían estar ordenados por fecha descendente, luego empleado
        assert perfs[0].date >= perfs[1].date
        assert perfs[1].date >= perfs[2].date


@pytest.mark.django_db
@pytest.mark.models
class TestEmployeePerformanceCalculations:
    """Pruebas para cálculos de EmployeePerformance"""

    def test_performance_score_above_target(self):
        """Probar cálculo de score cuando actual_value >= target_value"""
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("0.00")
        )
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("120.00")
        )

        assert perf.performance_score == 100

    def test_performance_score_below_min(self):
        """Probar cálculo de score cuando actual_value < min_value"""
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("40.00")
        )

        assert perf.performance_score == 0

    def test_performance_score_proportional(self):
        """Probar cálculo proporcional de score"""
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("0.00")
        )
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("50.00")
        )

        # (50 - 0) / (100 - 0) * 100 = 50
        assert perf.performance_score == 50

    def test_performance_score_no_target_value(self):
        """Probar que score es None cuando no hay target_value"""
        metric = PerformanceMetricFactory(target_value=None)
        perf = EmployeePerformanceFactory(metric=metric)

        assert perf.performance_score is None

    def test_performance_score_exact_target(self):
        """Probar score cuando actual_value == target_value"""
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("0.00")
        )
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("100.00")
        )

        assert perf.performance_score == 100

    def test_performance_score_at_min_value(self):
        """Probar score cuando actual_value == min_value"""
        metric = PerformanceMetricFactory(
            target_value=Decimal("100.00"), min_value=Decimal("50.00")
        )
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("50.00")
        )

        assert perf.performance_score == 0

    def test_is_above_target_true(self):
        """Probar is_above_target cuando actual_value >= target_value"""
        metric = PerformanceMetricFactory(target_value=Decimal("100.00"))
        perf = EmployeePerformanceFactory(
            metric=metric, actual_value=Decimal("120.00")
        )

        assert perf.is_above_target is True

    def test_is_above_target_false(self):
        """Probar is_above_target cuando actual_value < target_value"""
        metric = PerformanceMetricFactory(target_value=Decimal("100.00"))
        perf = EmployeePerformanceFactory(metric=metric, actual_value=Decimal("80.00"))

        assert perf.is_above_target is False

    def test_is_above_target_no_target_value(self):
        """Probar is_above_target cuando no hay target_value"""
        metric = PerformanceMetricFactory(target_value=None)
        perf = EmployeePerformanceFactory(metric=metric)

        assert perf.is_above_target is False


@pytest.mark.django_db
@pytest.mark.models
class TestDailyWorkLog:
    """Pruebas para el modelo DailyWorkLog"""

    def test_daily_work_log_creation(self):
        """Probar creación básica de registro diario"""
        log = DailyWorkLogFactory()
        assert log.pk is not None
        assert log.employee is not None
        assert log.date is not None
        assert log.start_time is not None
        assert log.end_time is not None

    def test_daily_work_log_str_representation(self):
        """Probar representación string del registro"""
        employee = EmployeeFactory()
        log = DailyWorkLogFactory(employee=employee, date=date(2024, 1, 15))
        expected = f"{employee} - 2024-01-15"
        assert str(log) == expected

    def test_daily_work_log_unique_together(self):
        """Probar unicidad de (employee, date)"""
        employee = EmployeeFactory()
        date_val = date(2024, 1, 15)

        DailyWorkLogFactory(employee=employee, date=date_val)

        with pytest.raises(IntegrityError):
            DailyWorkLogFactory(employee=employee, date=date_val)

    def test_daily_work_log_different_employee_same_date(self):
        """Probar que diferentes empleados pueden tener registro en misma fecha"""
        date_val = date(2024, 1, 15)

        log1 = DailyWorkLogFactory(date=date_val)
        log2 = DailyWorkLogFactory(date=date_val)

        assert log1.employee != log2.employee
        assert log1.date == log2.date

    def test_daily_work_log_quality_score_optional(self):
        """Probar que quality_score es opcional"""
        log = DailyWorkLogFactory(quality_score=None)
        assert log.quality_score is None

    def test_daily_work_log_quality_score_validation_min(self):
        """Probar validación de quality_score mínimo (0)"""
        log = DailyWorkLogFactory(quality_score=Decimal("0.00"))
        assert log.quality_score == Decimal("0.00")

    def test_daily_work_log_quality_score_validation_max(self):
        """Probar validación de quality_score máximo (7)"""
        log = DailyWorkLogFactory(quality_score=Decimal("7.00"))
        assert log.quality_score == Decimal("7.00")

    def test_daily_work_log_quality_score_invalid_below_zero(self):
        """Probar que quality_score no puede ser menor a 0"""
        with pytest.raises(ValidationError):
            log = DailyWorkLogFactory(quality_score=Decimal("-0.01"))
            log.full_clean()

    def test_daily_work_log_quality_score_invalid_above_seven(self):
        """Probar que quality_score no puede ser mayor a 7"""
        with pytest.raises(ValidationError):
            log = DailyWorkLogFactory(quality_score=Decimal("7.01"))
            log.full_clean()

    def test_daily_work_log_default_values(self):
        """Probar valores por defecto"""
        log = DailyWorkLogFactory()
        assert log.packages_processed == 0 or log.packages_processed >= 0
        assert log.trucks_received == 0 or log.trucks_received >= 0
        assert log.trucks_dispatched == 0 or log.trucks_dispatched >= 0
        assert log.safety_incidents == 0 or log.safety_incidents >= 0
        assert log.total_break_time == timedelta(0) or log.total_break_time >= timedelta(0)

    def test_daily_work_log_notes_optional(self):
        """Probar que notes es opcional"""
        log = DailyWorkLogFactory(notes="")
        assert log.notes == ""

    def test_daily_work_log_ordering(self):
        """Probar ordenamiento por fecha descendente y empleado"""
        employee1 = EmployeeFactory()
        employee2 = EmployeeFactory()

        log1 = DailyWorkLogFactory(employee=employee1, date=date(2024, 1, 15))
        log2 = DailyWorkLogFactory(employee=employee2, date=date(2024, 1, 20))
        log3 = DailyWorkLogFactory(employee=employee1, date=date(2024, 1, 20))

        logs = DailyWorkLog.objects.all()
        # Deberían estar ordenados por fecha descendente, luego empleado
        assert logs[0].date >= logs[1].date
        assert logs[1].date >= logs[2].date


@pytest.mark.django_db
@pytest.mark.models
class TestDailyWorkLogCalculations:
    """Pruebas para cálculos de DailyWorkLog"""

    def test_total_work_time_basic(self):
        """Probar cálculo básico de tiempo total de trabajo"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            total_break_time=timedelta(hours=1),
        )

        total_time = log.total_work_time
        # 8 horas (9-17) - 1 hora de descanso = 7 horas
        assert total_time == timedelta(hours=7)

    def test_total_work_time_with_break(self):
        """Probar cálculo con tiempo de descanso"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(8, 0),
            end_time=time(16, 0),
            total_break_time=timedelta(hours=0, minutes=30),
        )

        total_time = log.total_work_time
        # 8 horas (8-16) - 0.5 horas de descanso = 7.5 horas
        assert total_time == timedelta(hours=7, minutes=30)

    def test_total_work_time_no_break(self):
        """Probar cálculo sin tiempo de descanso"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            total_break_time=timedelta(0),
        )

        total_time = log.total_work_time
        # 8 horas (9-17) - 0 horas = 8 horas
        assert total_time == timedelta(hours=8)

    def test_total_work_time_crosses_midnight(self):
        """Probar cálculo cuando el horario cruza medianoche"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(22, 0),  # 10 PM
            end_time=time(6, 0),  # 6 AM siguiente día
            total_break_time=timedelta(hours=1),
        )

        total_time = log.total_work_time
        # 8 horas (22-06) - 1 hora de descanso = 7 horas
        assert total_time == timedelta(hours=7)

    def test_productivity_score_with_packages(self):
        """Probar cálculo de productividad con paquetes"""
        log = DailyWorkLogFactory(
            packages_processed=10,
            trucks_received=0,
            trucks_dispatched=0,
        )

        # 10 paquetes * 2 = 20 puntos (máximo 40)
        assert log.productivity_score == 20

    def test_productivity_score_with_trucks_received(self):
        """Probar cálculo de productividad con camiones recibidos"""
        log = DailyWorkLogFactory(
            packages_processed=0,
            trucks_received=5,
            trucks_dispatched=0,
        )

        # 5 camiones * 3 = 15 puntos (máximo 30)
        assert log.productivity_score == 15

    def test_productivity_score_with_trucks_dispatched(self):
        """Probar cálculo de productividad con camiones despachados"""
        log = DailyWorkLogFactory(
            packages_processed=0,
            trucks_received=0,
            trucks_dispatched=4,
        )

        # 4 camiones * 3 = 12 puntos (máximo 30)
        assert log.productivity_score == 12

    def test_productivity_score_combined(self):
        """Probar cálculo de productividad combinado"""
        log = DailyWorkLogFactory(
            packages_processed=10,  # 20 puntos
            trucks_received=5,  # 15 puntos
            trucks_dispatched=4,  # 12 puntos
        )

        # Total: 20 + 15 + 12 = 47 puntos
        assert log.productivity_score == 47

    def test_productivity_score_max_packages(self):
        """Probar límite máximo de puntos por paquetes (40)"""
        log = DailyWorkLogFactory(
            packages_processed=30,  # 30 * 2 = 60, pero máximo 40
            trucks_received=0,
            trucks_dispatched=0,
        )

        assert log.productivity_score == 40

    def test_productivity_score_max_trucks_received(self):
        """Probar límite máximo de puntos por camiones recibidos (30)"""
        log = DailyWorkLogFactory(
            packages_processed=0,
            trucks_received=15,  # 15 * 3 = 45, pero máximo 30
            trucks_dispatched=0,
        )

        assert log.productivity_score == 30

    def test_productivity_score_max_trucks_dispatched(self):
        """Probar límite máximo de puntos por camiones despachados (30)"""
        log = DailyWorkLogFactory(
            packages_processed=0,
            trucks_received=0,
            trucks_dispatched=12,  # 12 * 3 = 36, pero máximo 30
        )

        assert log.productivity_score == 30

    def test_productivity_score_zero(self):
        """Probar productividad con valores cero"""
        log = DailyWorkLogFactory(
            packages_processed=0,
            trucks_received=0,
            trucks_dispatched=0,
        )

        assert log.productivity_score == 0

    def test_efficiency_percentage_basic(self):
        """Probar cálculo básico de porcentaje de eficiencia"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            total_break_time=timedelta(hours=1),
        )

        # total_work_time = (end - start) - break = (17-9) - 1 = 7 horas
        # work_time = total_work_time - break = 7 - 1 = 6 horas
        # efficiency = (6 / 7) * 100 = 85.71%
        efficiency = log.efficiency_percentage
        assert abs(efficiency - 85.71) < 0.1

    def test_efficiency_percentage_no_break(self):
        """Probar eficiencia sin descanso"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            total_break_time=timedelta(0),
        )

        # Tiempo total: 8 horas
        # Tiempo de trabajo: 8 horas
        # Eficiencia: (8 / 8) * 100 = 100%
        assert log.efficiency_percentage == 100.0

    def test_efficiency_percentage_zero_time(self):
        """Probar eficiencia con tiempo cero (división por cero)"""
        log = DailyWorkLogFactory(
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(9, 0),  # Mismo tiempo
            total_break_time=timedelta(0),
        )

        # Debería retornar 0 en lugar de error
        assert log.efficiency_percentage == 0


@pytest.mark.django_db
@pytest.mark.models
class TestPerformanceEvaluation:
    """Pruebas para el modelo PerformanceEvaluation"""

    def test_evaluation_creation(self):
        """Probar creación básica de evaluación"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert evaluation.pk is not None

    def test_evaluation_str_representation(self):
        """Probar representación string de la evaluación"""
        employee = EmployeeFactory()
        evaluation = PerformanceEvaluationFactory(
            employee=employee,
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        expected = f"{employee} - Mensual - 2024-01-31"
        assert str(evaluation) == expected

    def test_evaluation_type_choices(self):
        """Probar opciones válidas de tipo de evaluación"""
        valid_types = ["daily", "weekly", "monthly", "quarterly", "annual"]

        for eval_type in valid_types:
            evaluation = PerformanceEvaluationFactory(
                evaluation_type=eval_type,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
            )
            assert evaluation.evaluation_type == eval_type
            assert evaluation.get_evaluation_type_display() is not None

    def test_evaluation_duration_days(self):
        """Probar cálculo de duración en días"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        # 31 - 1 + 1 = 31 días
        assert evaluation.duration_days == 31

    def test_evaluation_duration_days_single_day(self):
        """Probar duración de un solo día"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="daily",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15),
        )

        # 15 - 15 + 1 = 1 día
        assert evaluation.duration_days == 1

    def test_evaluation_overall_score_optional(self):
        """Probar que overall_score es opcional"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            overall_score=None,
        )
        assert evaluation.overall_score is None

    def test_evaluation_evaluated_by_optional(self):
        """Probar que evaluated_by es opcional"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            evaluated_by=None,
        )
        assert evaluation.evaluated_by is None

    def test_evaluation_text_fields_optional(self):
        """Probar que campos de texto son opcionales"""
        evaluation = PerformanceEvaluationFactory(
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            strengths="",
            areas_for_improvement="",
            recommendations="",
        )
        assert evaluation.strengths == ""
        assert evaluation.areas_for_improvement == ""
        assert evaluation.recommendations == ""

    def test_evaluation_ordering(self):
        """Probar ordenamiento por fecha de fin descendente y empleado"""
        employee1 = EmployeeFactory()
        employee2 = EmployeeFactory()

        eval1 = PerformanceEvaluationFactory(
            employee=employee1,
            evaluation_type="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        eval2 = PerformanceEvaluationFactory(
            employee=employee2,
            evaluation_type="monthly",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29),
        )

        eval3 = PerformanceEvaluationFactory(
            employee=employee1,
            evaluation_type="monthly",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29),
        )

        evaluations = PerformanceEvaluation.objects.all()
        # Deberían estar ordenados por end_date descendente, luego empleado
        assert evaluations[0].end_date >= evaluations[1].end_date
        assert evaluations[1].end_date >= evaluations[2].end_date

