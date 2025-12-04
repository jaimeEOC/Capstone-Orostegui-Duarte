# 🚀 Logistica HR - Instrucciones de Uso

## ⚡ Inicio Rápido

### Windows
```bash
# Ejecutar desde el directorio web_logistica
.\ejecutar.bat
```

### Linux/Mac
```bash
# Ejecutar desde el directorio web_logistica
./ejecutar.sh
```

### PowerShell (Windows)
```powershell
# Ejecutar desde el directorio web_logistica
.\ejecutar.ps1
```

## 🎯 ¿Qué hace el ejecutor?

El ejecutor automático realiza todos estos pasos:

1. ✅ **Verifica Python** (3.8+)
2. ✅ **Crea entorno virtual** (si no existe)
3. ✅ **Instala dependencias** automáticamente
4. ✅ **Configura base de datos** SQLite
5. ✅ **Crea usuario administrador**
6. ✅ **Inicia el servidor** Django

## 🌐 Acceso al Sistema

Una vez ejecutado, el sistema estará disponible en:

- **Página principal**: http://localhost:8000/
- **Panel de administración**: http://localhost:8000/admin/

### Credenciales por defecto:
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 📋 Funcionalidades del Sistema

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

## 🔧 Solución de Problemas

### Error: "Python no encontrado"
- Instala Python 3.8+ desde https://python.org
- Asegúrate de marcar "Add to PATH" durante la instalación

### Error: "No se puede activar entorno virtual"
- Ejecuta el script como administrador
- Verifica que no haya espacios en la ruta del proyecto

### Error: "Puerto 8000 en uso"
- Cierra otras aplicaciones que usen el puerto 8000
- O cambia el puerto en el comando final del script

## 📁 Estructura del Proyecto

```
web_logistica/
├── ejecutar.bat          # Ejecutor para Windows
├── ejecutar.ps1          # Ejecutor para PowerShell
├── ejecutar.sh           # Ejecutor para Linux/Mac
├── manage.py             # Script principal de Django
├── logistica_hr/         # Configuración del proyecto
├── templates/            # Plantillas HTML
├── static/               # Archivos estáticos
└── venv/                 # Entorno virtual (se crea automáticamente)
```

## 🛠️ Comandos Útiles

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
