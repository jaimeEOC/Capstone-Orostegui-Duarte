# Logistica HR - Sistema de Gestión de Personal para Logística

## 📋 Descripción

**Logistica HR** es una aplicación web desarrollada en Django para la gestión y evaluación de personal en el área de logística, diseñada para optimizar la productividad empresarial mediante el seguimiento de métricas clave como productividad, tiempos de ocio, carga laboral y cumplimiento de tareas.

## 🎯 Objetivos del Proyecto

### Objetivo General
Desarrollar una aplicación web de gestión y evaluación de personal para el área de logística, que permita medir productividad, generar estadísticas, y optimizar la toma de decisiones en la administración del recurso humano.

### Objetivos Específicos
- ✅ Implementar un sistema de calificación de empleados basado en criterios de productividad
- ✅ Desarrollar un módulo de seguimiento de carga laboral en tiempo real
- ✅ Generar reportes estadísticos diarios, semanales y mensuales
- ✅ Diseñar dashboards interactivos con KPIs clave
- ✅ Evaluar el impacto en la mejora de la gestión del personal

## 🏗️ Arquitectura del Sistema

### Tecnologías Utilizadas
- **Backend**: Django 4.2.7 + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Tareas Asíncronas**: Celery + Redis
- **Frontend**: React (preparado para integración)
- **Autenticación**: Sistema de usuarios personalizado con roles
- **API**: REST API con documentación automática

### Estructura del Proyecto
```
logistica_hr/
├── logistica_hr/          # Configuración principal del proyecto
├── logistica_hr/core/     # Funcionalidades base y modelos comunes
├── logistica_hr/users/    # Gestión de usuarios y autenticación
├── logistica_hr/employees/ # Gestión de empleados y departamentos
├── logistica_hr/tasks/    # Gestión de tareas y asignaciones
├── logistica_hr/performance/ # Métricas y evaluación de rendimiento
├── logistica_hr/reports/  # Generación y programación de reportes
└── static/                # Archivos estáticos
```

## 🚀 Características Principales

### 👥 Gestión de Usuarios
- Sistema de roles (Administrador, Supervisor, Empleado)
- Perfiles de usuario personalizables
- Gestión de departamentos y posiciones
- Control de acceso basado en roles

### 📊 Gestión de Empleados
- Registro completo de información laboral
- Horarios de trabajo configurables
- Habilidades y certificaciones
- Supervisor asignado

### 📋 Gestión de Tareas
- Asignación y seguimiento de tareas
- Categorización por prioridad y tipo
- Registro de tiempo dedicado
- Sistema de comentarios y notas

### 📈 Evaluación de Rendimiento
- Métricas personalizables (productividad, calidad, eficiencia)
- Registro diario de trabajo con KPIs
- Evaluaciones periódicas (diaria, semanal, mensual)
- Cálculo automático de puntajes

### 📊 Reportes y Analytics
- Plantillas de reportes configurables
- Generación automática programada
- Múltiples formatos (PDF, Excel, CSV, JSON)
- Dashboards con indicadores clave

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- Redis (para Celery)
- Node.js 16+ (para frontend)

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd logistica_hr
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=logistica_hr
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb logistica_hr

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar el Proyecto
```bash
# Terminal 1: Servidor Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A logistica_hr worker -l info

# Terminal 3: Celery Beat (para tareas programadas)
celery -A logistica_hr beat -l info
```

## 📱 Uso del Sistema

### Acceso al Sistema
- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/v1/

### Roles y Permisos

#### 👑 Administrador
- Acceso completo al sistema
- Gestión de usuarios y roles
- Configuración del sistema
- Generación de reportes

#### 👨‍💼 Supervisor
- Gestión de empleados asignados
- Asignación de tareas
- Evaluación de rendimiento
- Generación de reportes de equipo

#### 👷 Empleado
- Visualización de tareas asignadas
- Registro de tiempo de trabajo
- Actualización de estado de tareas
- Visualización de métricas personales

## 🔧 API Endpoints

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

### Reportes
- `GET /api/v1/reports/` - Listar reportes
- `POST /api/v1/reports/generate/` - Generar reporte
- `GET /api/v1/reports/{id}/download/` - Descargar reporte

## 📊 Métricas y KPIs

### Productividad
- Paquetes procesados por hora
- Camiones recibidos/despachados
- Tiempo promedio por tarea
- Eficiencia del tiempo de trabajo

### Calidad
- Puntaje de calidad por tarea
- Errores reportados
- Satisfacción del cliente
- Cumplimiento de estándares

### Asistencia
- Horas trabajadas vs. programadas
- Tiempo de descanso
- Puntualidad
- Ausencias no justificadas

### Seguridad
- Incidentes reportados
- Cumplimiento de protocolos
- Capacitaciones completadas
- Uso de equipos de protección

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests unitarios
python manage.py test

# Tests con cobertura
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Estructura de Tests
- Tests unitarios para modelos
- Tests de integración para APIs
- Tests de permisos y autenticación
- Tests de servicios y utilidades

## 🚀 Despliegue

### Configuración de Producción
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=clave-secreta-produccion
DJANGO_ALLOWED_HOSTS=tu-dominio.com

# Configuración de base de datos
DB_NAME=logistica_hr_prod
DB_USER=usuario_produccion
DB_PASSWORD=password_seguro
DB_HOST=localhost

# Configuración de Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Comandos de Despliegue
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones
python manage.py migrate

# Crear superusuario si es necesario
python manage.py createsuperuser

# Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart redis
```

## 📈 Roadmap y Mejoras Futuras

### Fase 2 (Próximas Versiones)

### Fase 3 (Versiones Avanzadas)

## 🤝 Contribución

### Cómo Contribuir
1. Fork del proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- Seguir PEP 8 para Python
- Usar docstrings para documentar funciones
- Escribir tests para nuevas funcionalidades
- Mantener cobertura de código > 80%


## 👥 Autores

- **Desarrollador**: Jaime Oróstegui y Jazmín Duarte
- **Universidad**: DuocUC
- **Año**: 2025


---

**Logistica HR** - Transformando la gestión de personal en logística 🚀


