# 🚀 Guía de Ejecución - Logistica HR

## 📋 Resumen Rápido

Este proyecto es un sistema de gestión de personal para logística desarrollado en Django. Esta guía te ayudará a ejecutarlo paso a paso.

## 🎯 Opciones de Instalación

### Opción 1: Instalación Simple (Recomendada para desarrollo)
- ✅ **Base de datos**: SQLite (no requiere instalación adicional)
- ✅ **Sin Redis/Celery**: Para desarrollo básico
- ✅ **Fácil de configurar**: Ideal para empezar

### Opción 2: Instalación Completa (Para producción)
- ⚙️ **Base de datos**: PostgreSQL
- ⚙️ **Redis**: Para tareas asíncronas
- ⚙️ **Celery**: Para procesamiento en segundo plano

---

## 🚀 OPCIÓN 1: Instalación Simple (Recomendada)

### ⚡ Instalación Automática (Más Fácil)

#### Windows
```bash
# 1. Navegar al directorio del proyecto
cd web_logistica

# 2. Ejecutar script de instalación
.\instalar.bat
```

#### Linux/Mac
```bash
# 1. Navegar al directorio del proyecto
cd web_logistica

# 2. Ejecutar script de instalación
./instalar.sh
```

### ⚙️ Instalación Manual (Paso a paso)

#### 1. Prerrequisitos
- ✅ Python 3.8+ instalado
- ✅ Git (opcional, para clonar)

#### 2. Navegar al directorio del proyecto
```bash
cd web_logistica
```

#### 3. Activar entorno virtual
```bash
# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

#### 4. Instalar dependencias
```bash
pip install -r requirements-windows-simple.txt
```

#### 5. Configurar base de datos
```bash
python manage.py makemigrations --settings=logistica_hr.settings_sqlite
python manage.py migrate --settings=logistica_hr.settings_sqlite
```

#### 6. Crear superusuario
```bash
python create_superuser.py
```

#### 7. Ejecutar servidor
```bash
python manage.py runserver --settings=logistica_hr.settings_sqlite
```

#### 8. Acceder al sistema
- **Página principal**: http://localhost:8000/
- **Panel de administración**: http://localhost:8000/admin/
  - Usuario: `admin`
  - Contraseña: `admin123`

---

## ⚙️ OPCIÓN 2: Instalación Completa

### 1. Prerrequisitos
- ✅ Python 3.8+
- ✅ PostgreSQL 12+
- ✅ Redis (opcional)

### 2. Navegar al directorio del proyecto
```bash
cd web_logistica
```

### 3. Activar entorno virtual
```bash
# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
# Para Windows (si tienes problemas con psycopg2)
pip install -r requirements-windows.txt
pip install psycopg2-binary

# Para Linux/Mac
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crear archivo `.env`:
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

### 6. Configurar base de datos
```bash
# Crear base de datos PostgreSQL
createdb logistica_hr

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario
```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor
```bash
# Terminal 1: Servidor Django
python manage.py runserver

# Terminal 2: Celery Worker (opcional)
celery -A logistica_hr worker -l info

# Terminal 3: Celery Beat (opcional)
celery -A logistica_hr beat -l info
```

---

## 📁 Explicación de Archivos de Requirements

### `requirements-windows-simple.txt` ⭐ (Recomendado)
- **Para**: Desarrollo simple en Windows
- **Incluye**: Django, DRF, dependencias básicas
- **Excluye**: PostgreSQL, Redis, Celery
- **Ventaja**: Instalación rápida, sin problemas de compilación

### `requirements-windows.txt`
- **Para**: Windows con PostgreSQL
- **Incluye**: Todas las dependencias excepto psycopg2-binary
- **Nota**: Instalar psycopg2-binary por separado

### `requirements.txt`
- **Para**: Linux/Mac o Windows con todas las dependencias
- **Incluye**: Todas las dependencias completas
- **Requisito**: Tener PostgreSQL y Redis instalados

---

## 🔧 Comandos Útiles

### Verificar instalación
```bash
python manage.py check --settings=logistica_hr.settings_sqlite
```

### Crear migraciones
```bash
python manage.py makemigrations --settings=logistica_hr.settings_sqlite
```

### Aplicar migraciones
```bash
python manage.py migrate --settings=logistica_hr.settings_sqlite
```

### Crear superusuario manualmente
```bash
python manage.py createsuperuser --settings=logistica_hr.settings_sqlite
```

### Ejecutar tests
```bash
python manage.py test --settings=logistica_hr.settings_sqlite
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
# Verificar que el entorno virtual esté activo
# Reinstalar Django
pip install Django==4.2.7
```

### Error: "can't open file 'manage.py'"
```bash
# Asegurarse de estar en el directorio correcto
cd web_logistica
ls  # Debe mostrar manage.py
```

### Error de base de datos
```bash
# Usar configuración SQLite
python manage.py runserver --settings=logistica_hr.settings_sqlite
```

### Error de archivos estáticos
```bash
# Crear directorio static
mkdir static
```

---

## 📊 Estructura del Proyecto

```
web_logistica/
├── manage.py                    # Script principal de Django
├── requirements-windows-simple.txt  # ⭐ Dependencias simples
├── requirements-windows.txt     # Dependencias para Windows
├── requirements.txt            # Dependencias completas
├── settings_sqlite.py          # Configuración para SQLite
├── settings.py                 # Configuración para PostgreSQL
├── create_superuser.py         # Script para crear superusuario
├── logistica_hr/              # Configuración principal
├── templates/                  # Plantillas HTML
├── venv/                      # Entorno virtual
└── db.sqlite3                 # Base de datos SQLite
```

---

## 🎯 URLs del Sistema

- **🏠 Página principal**: http://localhost:8000/
- **⚙️ Panel de administración**: http://localhost:8000/admin/
- **👥 Empleados**: http://localhost:8000/employees/
- **📋 Tareas**: http://localhost:8000/tasks/
- **📊 Rendimiento**: http://localhost:8000/performance/
- **📈 Reportes**: http://localhost:8000/reports/
- **🔌 API REST**: http://localhost:8000/api/v1/

---

## 👥 Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: `admin123`

---

## 📞 Soporte

Si tienes problemas:

1. **Verificar Python**: `python --version` (debe ser 3.8+)
2. **Verificar directorio**: Debe estar en `web_logistica/`
3. **Verificar entorno virtual**: Debe estar activo
4. **Usar configuración SQLite**: `--settings=logistica_hr.settings_sqlite`

---

**¡Logistica HR - Transformando la gestión de personal en logística! 🚀**
