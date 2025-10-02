# Guía de Testing - Logistica HR

## Resumen

Este documento describe cómo ejecutar y mantener las pruebas automatizadas del proyecto Logistica HR.

## Inicio Rápido

### Ejecutar todas las pruebas
```bash
# Windows
run_tests.bat

# Linux/Mac
python run_tests.py
```

### Ejecutar con cobertura
```bash
python run_tests.py --coverage
```

### Instalar dependencias y ejecutar
```bash
python run_tests.py --install --coverage
```

## Estructura de Pruebas

```
tests/
├── conftest.py                 # Configuración global de pytest
├── factories.py               # Factory Boy para datos de prueba
├── unit/                      # Pruebas unitarias
│   ├── test_models/           # Pruebas de modelos
│   ├── test_views/            # Pruebas de vistas
│   └── test_middleware/       # Pruebas de middleware
├── integration/               # Pruebas de integración
├── e2e/                      # Pruebas end-to-end
└── fixtures/                 # Datos de prueba estáticos
```

## Tipos de Pruebas

### Pruebas Unitarias
- **Modelos**: Validación de datos, relaciones, métodos
- **Middleware**: Autenticación, permisos, redirecciones
- **Vistas**: Lógica de presentación, respuestas HTTP

### Pruebas de Integración
- **Flujos de autenticación**: Login/logout completos
- **APIs**: Endpoints REST con datos reales
- **Base de datos**: Operaciones CRUD complejas

### Pruebas End-to-End
- **Flujos de usuario**: Navegación completa
- **Dashboards**: Funcionalidad por rol
- **Formularios**: Validación en tiempo real

## Comandos Disponibles

### Ejecutar por tipo
```bash
# Solo pruebas unitarias
python run_tests.py --type unit

# Solo pruebas de integración
python run_tests.py --type integration

# Solo pruebas end-to-end
python run_tests.py --type e2e
```

### Ejecutar por marcador
```bash
# Solo pruebas de modelos
python run_tests.py --marker models

# Solo pruebas de middleware
python run_tests.py --marker middleware

# Solo pruebas de API
python run_tests.py --marker api
```

### Ejecutar pruebas específicas
```bash
# Archivo específico
python run_tests.py --path tests/unit/test_models/test_user_model.py

# Función específica
python run_tests.py --path tests/unit/test_models/test_user_model.py::TestUserModel::test_user_creation
```

### Con cobertura
```bash
# Reporte HTML
python run_tests.py --coverage

# Solo terminal
python -m pytest tests/ --cov=logistica_hr --cov-report=term-missing
```

## Cobertura de Código

### Objetivos de Cobertura
- **Modelos**: 90%+
- **Middleware**: 95%+
- **Vistas**: 80%+
- **APIs**: 85%+

### Ver reporte HTML
```bash
# Generar reporte
python run_tests.py --coverage

# Abrir en navegador
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

## Configuración

### Archivos de configuración
- `pytest.ini`: Configuración de pytest
- `.coveragerc`: Configuración de cobertura
- `conftest.py`: Fixtures globales
- `factories.py`: Factories para datos de prueba

### Variables de entorno
```bash
# Para testing
DJANGO_SETTINGS_MODULE=logistica_hr.settings_sqlite
```

## Escribir Nuevas Pruebas

### Estructura básica
```python
import pytest
from tests.factories import UserFactory

@pytest.mark.django_db
@pytest.mark.models
class TestMiModelo:
    def test_creacion_basica(self):
        """Probar creación básica"""
        obj = UserFactory()
        assert obj.pk is not None
```

### Marcadores disponibles
- `@pytest.mark.unit`: Pruebas unitarias
- `@pytest.mark.integration`: Pruebas de integración
- `@pytest.mark.e2e`: Pruebas end-to-end
- `@pytest.mark.models`: Pruebas de modelos
- `@pytest.mark.views`: Pruebas de vistas
- `@pytest.mark.middleware`: Pruebas de middleware
- `@pytest.mark.api`: Pruebas de API
- `@pytest.mark.slow`: Pruebas lentas

### Fixtures disponibles
- `admin_user`: Usuario administrador
- `supervisor_user`: Usuario supervisor
- `employee_user`: Usuario empleado
- `request_factory`: Factory para requests
- `authenticated_request`: Request autenticado
- `unauthenticated_request`: Request no autenticado

## Solución de Problemas

### Error: "No module named 'pytest'"
```bash
# Instalar dependencias
pip install -r requirements-testing.txt
```

### Error: "Database access not allowed"
```bash
# Verificar que las pruebas usen @pytest.mark.django_db
@pytest.mark.django_db
def test_mi_funcion():
    pass
```

### Error: "Factory not found"
```bash
# Verificar que el factory esté importado
from tests.factories import UserFactory
```

### Pruebas lentas
```bash
# Ejecutar solo pruebas rápidas
python -m pytest tests/ -m "not slow"

# Ejecutar en paralelo
python -m pytest tests/ -n auto
```

## Métricas y Reportes

### Reporte de cobertura
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml`
- **Terminal**: Salida en consola

### Logs de pytest
```bash
# Verbose
python -m pytest tests/ -v

# Con información de tiempo
python -m pytest tests/ --durations=10

# Con información de cobertura
python -m pytest tests/ --cov=logistica_hr --cov-report=term-missing
```

## Integración Continua

### GitHub Actions (futuro)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements-testing.txt
      - name: Run tests
        run: python run_tests.py --coverage
```

## Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [pytest-django](https://pytest-django.readthedocs.io/)

## Contribuir

1. Escribe pruebas para nueva funcionalidad
2. Asegúrate de que todas las pruebas pasen
3. Mantén la cobertura de código alta
4. Documenta casos de prueba complejos
5. Actualiza este archivo si es necesario
