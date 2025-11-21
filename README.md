# Logistica HR - Sistema de Gestión de Personal para Logística

Aplicación web desarrollada en Django para la gestión y evaluación de personal en el área de logística. Permite medir productividad, generar estadísticas y optimizar la toma de decisiones en la administración del recurso humano.

## Descripción

Sistema de gestión de personal que optimiza la productividad empresarial mediante el seguimiento de métricas clave como productividad, tiempos de trabajo, carga laboral y cumplimiento de tareas.

## Objetivos

- Implementar un sistema de calificación de empleados basado en criterios de productividad
- Desarrollar un módulo de seguimiento de carga laboral en tiempo real
- Generar reportes estadísticos diarios, semanales y mensuales
- Diseñar dashboards interactivos con KPIs clave
- Evaluar el impacto en la mejora de la gestión del personal

## Tecnologías

- Backend: Django 4.2.7 + Django REST Framework
- Base de Datos: PostgreSQL (SQLite para desarrollo)
- Tareas Asíncronas: Celery + Redis
- Generación de PDF: ReportLab
- Testing: pytest + pytest-django + Factory Boy
- Frontend: HTML/CSS/JavaScript (templates Django)

## Estructura del Proyecto

```
web_logistica/
├── logistica_hr/
│   ├── settings/          # Configuración modular (base, development, production)
│   ├── core/             # Dashboards, vistas principales, middleware
│   ├── users/             # Gestión de usuarios y autenticación
│   ├── employees/        # Gestión de empleados y departamentos
│   ├── tasks/             # Gestión de tareas y asignaciones
│   ├── performance/       # Métricas y evaluación de rendimiento
│   └── reports/           # Generación y programación de reportes
├── templates/             # Plantillas HTML
├── static/               # Archivos estáticos
├── tests/                # Pruebas unitarias
└── manage.py             # Script de gestión de Django
```

## Características Principales

### Gestión de Usuarios
- Sistema de roles (Administrador, Supervisor, Empleado)
- Autenticación con email
- Perfiles personalizables
- Control de acceso basado en roles

### Gestión de Empleados
- CRUD completo de empleados y supervisores
- Asignación de supervisores
- Departamentos y posiciones
- Habilidades y certificaciones

### Gestión de Tareas
- Asignación y seguimiento de tareas
- Estados: pendiente, en progreso, completada
- Prioridades y categorías
- Seguimiento de tiempo

### Evaluación de Rendimiento
- Registro diario de trabajo (DailyWorkLog)
- Métricas: paquetes procesados, camiones recibidos/despachados, calidad, incidentes
- Cálculo automático de promedios
- Evaluaciones semanales y mensuales

### Reportes y Dashboards
- Dashboards por rol con KPIs
- Reportes semanales y mensuales
- Generación de PDF de reportes
- Gráficos de rendimiento
- Tablas de rendimiento por empleado

## Instalación

### Requisitos
- Python 3.8+
- PostgreSQL 12+ (opcional, SQLite por defecto)
- Redis (opcional, para Celery)

### Instalación Rápida

#### Windows
```bash
cd web_logistica
.\instalar.bat
```

#### Linux/Mac
```bash
cd web_logistica
./instalar.sh
```

### Instalación Manual

```bash
# 1. Navegar al directorio
cd web_logistica

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements-windows-simple.txt

# 4. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python create_superuser.py

# 6. Ejecutar servidor
python manage.py runserver
```

## Acceso al Sistema

- URL: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Credenciales por defecto:
  - Usuario: `admin`
  - Contraseña: `admin123`

## Roles y Permisos

### Administrador
- Acceso completo al sistema
- Gestión de usuarios y roles
- Edición y eliminación de empleados y supervisores
- Configuración del sistema
- Generación de reportes

### Supervisor
- Gestión de empleados asignados
- Asignación de tareas
- Evaluación de rendimiento
- Generación de reportes de equipo (incluye PDF)
- Visualización de métricas del equipo

### Empleado
- Visualización de tareas asignadas
- Registro de tiempo de trabajo
- Actualización de estado de tareas
- Visualización de métricas personales

## Archivos de Requirements

- `requirements-windows-simple.txt`: Dependencias básicas (recomendado para desarrollo)
- `requirements-windows.txt`: Dependencias para Windows + PostgreSQL
- `requirements.txt`: Dependencias completas (producción)

## Testing

```bash
# Ejecutar tests
pytest

# Tests con cobertura
pytest --cov=logistica_hr --cov-report=html
```

## Comandos Útiles

```bash
# Verificar instalación
python manage.py check

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

# Crear superusuario
python manage.py createsuperuser
```

## Métricas y KPIs

- Paquetes procesados
- Camiones recibidos/despachados
- Calidad promedio (quality_score)
- Incidentes de seguridad
- Días trabajados
- Promedios diarios/semanales/mensuales

## API Endpoints

### Usuarios
- `GET /api/v1/users/` - Listar usuarios
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}/` - Obtener usuario
- `PUT /api/v1/users/{id}/` - Actualizar usuario
- `DELETE /api/v1/users/{id}/` - Eliminar usuario

### Empleados
- `GET /api/v1/employees/` - Listar empleados
- `POST /api/v1/employees/` - Crear empleado
- `GET /api/v1/employees/{id}/` - Obtener empleado
- `PUT /api/v1/employees/{id}/` - Actualizar empleado

### Tareas
- `GET /api/v1/tasks/` - Listar tareas
- `POST /api/v1/tasks/` - Crear tarea
- `GET /api/v1/tasks/{id}/` - Obtener tarea
- `PUT /api/v1/tasks/{id}/` - Actualizar tarea

### Rendimiento
- `GET /api/v1/performance/` - Métricas de rendimiento
- `POST /api/v1/performance/` - Registrar métrica
- `GET /api/v1/performance/daily-log/` - Registro diario

## Despliegue

### Configuración de Producción

Crear archivo `.env`:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=clave-secreta-produccion
DJANGO_ALLOWED_HOSTS=tu-dominio.com

DB_NAME=logistica_hr_prod
DB_USER=usuario_produccion
DB_PASSWORD=password_seguro
DB_HOST=localhost

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Comandos de Despliegue

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones
python manage.py migrate

# Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

## Autores

- Jaime Oróstegui
- Jazmín Duarte

Universidad: DuocUC  
Año: 2025
