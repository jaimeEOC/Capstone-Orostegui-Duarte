#!/bin/bash

# Logistica HR - Ejecutor Automático (Linux/Mac)
# Sistema de Gestión de Personal para Logística

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}========================================"
echo -e "    LOGISTICA HR - EJECUTOR AUTOMATICO"
echo -e "========================================${NC}"
echo ""

# Función para mostrar errores
show_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Verificar Python
echo -e "${YELLOW}[1/8] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    show_error "Python3 no está instalado. Por favor instala Python 3.8+"
fi
python3 --version
show_success "Python encontrado"

# Verificar directorio
echo ""
echo -e "${YELLOW}[2/8] Verificando directorio del proyecto...${NC}"
if [ ! -f "manage.py" ]; then
    show_error "No se encuentra manage.py. Asegúrate de ejecutar este script desde el directorio web_logistica"
fi
show_success "Directorio correcto"

# Crear entorno virtual si no existe
echo ""
echo -e "${YELLOW}[3/8] Configurando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    show_success "Entorno virtual creado"
else
    show_success "Entorno virtual ya existe"
fi

# Activar entorno virtual
echo ""
echo -e "${YELLOW}[4/8] Activando entorno virtual...${NC}"
source venv/bin/activate
show_success "Entorno virtual activado"

# Instalar dependencias
echo ""
echo -e "${YELLOW}[5/8] Instalando dependencias...${NC}"
pip install -r requirements-windows-simple.txt --quiet
show_success "Dependencias instaladas"

# Configurar base de datos
echo ""
echo -e "${YELLOW}[6/8] Configurando base de datos...${NC}"
python manage.py makemigrations --settings=logistica_hr.settings_sqlite --noinput
python manage.py migrate --settings=logistica_hr.settings_sqlite --noinput
show_success "Base de datos configurada"

# Crear superusuario
echo ""
echo -e "${YELLOW}[7/8] Configurando usuario administrador...${NC}"
python3 crear_admin.py
show_success "Usuario administrador configurado"

# Iniciar servidor
echo ""
echo -e "${YELLOW}[8/8] Iniciando servidor...${NC}"
echo ""
echo -e "${GREEN}========================================"
echo -e "    SISTEMA INICIADO EXITOSAMENTE"
echo -e "========================================${NC}"
echo ""
echo -e "El servidor se ejecutará en:"
echo -e "${CYAN}- Página principal: http://localhost:8000/${NC}"
echo -e "${CYAN}- Panel de administración: http://localhost:8000/admin/${NC}"
echo ""
echo -e "Credenciales de acceso:"
echo -e "${YELLOW}- Usuario: admin${NC}"
echo -e "${YELLOW}- Contraseña: admin123${NC}"
echo ""
echo -e "${RED}Presiona Ctrl+C para detener el servidor${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

python manage.py runserver --settings=logistica_hr.settings_sqlite
