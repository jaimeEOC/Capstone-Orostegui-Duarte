#!/bin/bash

echo "========================================"
echo "   LOGISTICA HR - INSTALACION AUTOMATICA"
echo "========================================"
echo

echo "[1/6] Verificando Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python no está instalado o no está en el PATH"
    exit 1
fi

echo
echo "[2/6] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo activar el entorno virtual"
    exit 1
fi

echo
echo "[3/6] Instalando dependencias..."
pip install -r requirements-windows-simple.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi

echo
echo "[4/6] Configurando base de datos..."
cd web_logistica
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo configurar la base de datos"
    exit 1
fi

echo
echo "[5/6] Creando superusuario..."
python create_superuser.py
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el superusuario"
    exit 1
fi

echo
echo "[6/6] Iniciando servidor..."
echo
echo "========================================"
echo "   INSTALACION COMPLETADA EXITOSAMENTE"
echo "========================================"
echo
echo "El servidor se iniciará en:"
echo "- Página principal: http://localhost:8000/"
echo "- Panel de administración: http://localhost:8000/admin/"
echo
echo "Credenciales:"
echo "- Usuario: admin"
echo "- Contraseña: admin123"
echo
echo "Presiona Ctrl+C para detener el servidor"
echo "========================================"
echo

cd web_logistica
python manage.py runserver
