# 🚀 Logistica HR - Sistema de Gestión de Personal

**Sistema de gestión y evaluación de personal para logística desarrollado en Django.**

## ⚡ Inicio Rápido

### Windows
```bash
cd web_logistica
.\ejecutar.bat
```

### Linux/Mac
```bash
cd web_logistica
./ejecutar.sh
```

### PowerShell (Windows)
```powershell
cd web_logistica
.\ejecutar.ps1
```

## 🌐 Acceso al Sistema

- **Página principal**: http://localhost:8000/
- **Panel de administración**: http://localhost:8000/admin/

**Credenciales por defecto:**
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 📋 Funcionalidades

### 👑 Administrador
- Gestión completa de usuarios
- Configuración del sistema
- Acceso a todos los módulos

### 👨‍💼 Supervisor
- Gestión de empleados asignados
- Asignación de tareas
- Evaluación de rendimiento
- Reportes de equipo

### 👷 Empleado
- Visualización de tareas asignadas
- Registro de tiempo de trabajo
- Actualización de estado de tareas
- Métricas personales

## 🛠️ Estructura del Proyecto

```
web_logistica/
├── ejecutar.bat          # Ejecutor para Windows
├── ejecutar.ps1          # Ejecutor para PowerShell
├── ejecutar.sh           # Ejecutor para Linux/Mac
├── crear_admin.py        # Script para crear usuario admin
├── manage.py             # Script principal de Django
├── logistica_hr/         # Configuración del proyecto
├── templates/            # Plantillas HTML
├── static/               # Archivos estáticos
├── tests/                # Pruebas automatizadas
└── venv/                 # Entorno virtual
```

## 🔧 Comandos Útiles

### Verificar instalación
```bash
python manage.py check
```

### Crear migraciones
```bash
python manage.py makemigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Ejecutar tests
```bash
python manage.py test
```

## 📞 Soporte

Si tienes problemas:

1. **Verifica Python**: `python --version` (debe ser 3.8+)
2. **Verifica directorio**: Debe estar en `web_logistica/`
3. **Ejecuta como administrador** (Windows)
4. **Revisa los logs** en la consola

---

**Logistica HR** - Sistema de Gestión de Personal para Logística 🚀

**Desarrollado por**: Jaime Oróstegui y Jazmín Duarte  
**Universidad**: DuocUC  
**Año**: 2025