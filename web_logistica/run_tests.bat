@echo off
REM Script para ejecutar pruebas automatizadas en Windows
REM Uso: run_tests.bat [opciones]

echo Logistica HR - Sistema de Pruebas Automatizadas
echo ============================================================

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo No se encontró el entorno virtual. Ejecuta primero instalar.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar el script de Python con los argumentos pasados
python run_tests.py %*

REM Pausa para ver resultados
pause
