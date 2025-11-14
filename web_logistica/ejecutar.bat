@echo off
chcp 65001 >nul
title Logistica HR - Sistema de Gestion de Personal

echo.
echo ========================================
echo    LOGISTICA HR - EJECUTOR AUTOMATICO
echo ========================================
echo.

:: Verificar Python
echo [1/8] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
python --version
echo ✓ Python encontrado

:: Verificar directorio
echo.
echo [2/8] Verificando directorio del proyecto...
if not exist "manage.py" (
    echo ERROR: No se encuentra manage.py
    echo Asegurate de ejecutar este script desde el directorio web_logistica
    pause
    exit /b 1
)
echo ✓ Directorio correcto

:: Crear entorno virtual si no existe
echo.
echo [3/8] Configurando entorno virtual...
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✓ Entorno virtual creado
) else (
    echo ✓ Entorno virtual ya existe
)

:: Activar entorno virtual
echo.
echo [4/8] Activando entorno virtual...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo ✓ Entorno virtual activado

:: Instalar dependencias
echo.
echo [5/8] Instalando dependencias...
pip install -r requirements-windows-simple.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas

:: Configurar base de datos
echo.
echo [6/8] Configurando base de datos...
python manage.py makemigrations --noinput
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo ERROR: No se pudo configurar la base de datos
    pause
    exit /b 1
)
echo ✓ Base de datos configurada

:: Crear superusuario
echo.
echo [7/8] Configurando usuario administrador...
python crear_admin.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el usuario administrador
    pause
    exit /b 1
)
echo ✓ Usuario administrador configurado

:: Iniciar servidor
echo.
echo [8/8] Iniciando servidor...
echo.
echo ========================================
echo    SISTEMA INICIADO EXITOSAMENTE
echo ========================================
echo.
echo El servidor se ejecutara en:
echo - Pagina principal: http://localhost:8000/
echo - Panel de administracion: http://localhost:8000/admin/
echo.
echo Credenciales de acceso:
echo - Usuario: admin
echo - Contraseña: admin123
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python manage.py runserver
