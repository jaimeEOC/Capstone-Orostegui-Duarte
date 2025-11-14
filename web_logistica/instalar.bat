@echo off
echo ========================================
echo    LOGISTICA HR - INSTALACION AUTOMATICA
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo.
echo [2/6] Activando entorno virtual...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo.
echo [3/6] Instalando dependencias...
pip install -r requirements-windows-simple.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo [4/6] Configurando base de datos...
cd web_logistica
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: No se pudo configurar la base de datos
    pause
    exit /b 1
)

echo.
echo [5/6] Creando superusuario...
python create_superuser.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el superusuario
    pause
    exit /b 1
)

echo.
echo [6/6] Iniciando servidor...
echo.
echo ========================================
echo    INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo El servidor se iniciara en:
echo - Pagina principal: http://localhost:8000/
echo - Panel de administracion: http://localhost:8000/admin/
echo.
echo Credenciales:
echo - Usuario: admin
echo - Contraseña: admin123
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

cd web_logistica
python manage.py runserver
