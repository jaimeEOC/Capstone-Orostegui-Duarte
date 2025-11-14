#!/usr/bin/env python
"""
Script para crear usuario administrador
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@logistica.com', 'admin123')
    print('Usuario administrador creado')
else:
    print('Usuario administrador ya existe')
