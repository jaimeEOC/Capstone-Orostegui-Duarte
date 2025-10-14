# Logistica HR - Ejecutor Automático (PowerShell)
# Sistema de Gestión de Personal para Logística

param(
    [switch]$SkipDependencies,
    [switch]$SkipMigrations,
    [switch]$SkipUser
)

# Configurar codificación UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Logistica HR - Sistema de Gestion de Personal"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    LOGISTICA HR - EJECUTOR AUTOMATICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para mostrar errores
function Show-Error {
    param($Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Función para mostrar éxito
function Show-Success {
    param($Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

# Verificar Python
Write-Host "[1/8] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-Error "Python no esta instalado o no esta en el PATH. Por favor instala Python 3.8+ desde https://python.org"
    }
    Write-Host $pythonVersion
    Show-Success "Python encontrado"
} catch {
    Show-Error "Error al verificar Python: $_"
}

# Verificar directorio
Write-Host ""
Write-Host "[2/8] Verificando directorio del proyecto..." -ForegroundColor Yellow
if (-not (Test-Path "manage.py")) {
    Show-Error "No se encuentra manage.py. Asegurate de ejecutar este script desde el directorio web_logistica"
}
Show-Success "Directorio correcto"

# Crear entorno virtual si no existe
Write-Host ""
Write-Host "[3/8] Configurando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Show-Error "No se pudo crear el entorno virtual"
    }
    Show-Success "Entorno virtual creado"
} else {
    Show-Success "Entorno virtual ya existe"
}

# Activar entorno virtual
Write-Host ""
Write-Host "[4/8] Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Show-Error "No se pudo activar el entorno virtual"
}
Show-Success "Entorno virtual activado"

# Instalar dependencias
if (-not $SkipDependencies) {
    Write-Host ""
    Write-Host "[5/8] Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements-windows-simple.txt --quiet
    if ($LASTEXITCODE -ne 0) {
        Show-Error "No se pudieron instalar las dependencias"
    }
    Show-Success "Dependencias instaladas"
} else {
    Write-Host ""
    Write-Host "[5/8] Saltando instalacion de dependencias..." -ForegroundColor Yellow
}

# Configurar base de datos
if (-not $SkipMigrations) {
    Write-Host ""
    Write-Host "[6/8] Configurando base de datos..." -ForegroundColor Yellow
    python manage.py makemigrations --settings=logistica_hr.settings_sqlite --noinput
    python manage.py migrate --settings=logistica_hr.settings_sqlite --noinput
    if ($LASTEXITCODE -ne 0) {
        Show-Error "No se pudo configurar la base de datos"
    }
    Show-Success "Base de datos configurada"
} else {
    Write-Host ""
    Write-Host "[6/8] Saltando configuracion de base de datos..." -ForegroundColor Yellow
}

# Crear superusuario
if (-not $SkipUser) {
    Write-Host ""
    Write-Host "[7/8] Configurando usuario administrador..." -ForegroundColor Yellow
    python crear_admin.py
    if ($LASTEXITCODE -ne 0) {
        Show-Error "No se pudo crear el usuario administrador"
    }
    Show-Success "Usuario administrador configurado"
} else {
    Write-Host ""
    Write-Host "[7/8] Saltando creacion de usuario..." -ForegroundColor Yellow
}

# Iniciar servidor
Write-Host ""
Write-Host "[8/8] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    SISTEMA INICIADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "El servidor se ejecutara en:" -ForegroundColor White
Write-Host "- Pagina principal: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "- Panel de administracion: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credenciales de acceso:" -ForegroundColor White
Write-Host "- Usuario: admin" -ForegroundColor Yellow
Write-Host "- Contraseña: admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

python manage.py runserver --settings=logistica_hr.settings_sqlite