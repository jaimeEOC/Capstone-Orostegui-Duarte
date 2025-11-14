"""
Configuración de producción para Logistica HR
Usa PostgreSQL y tiene DEBUG=False
"""

from decouple import config
from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    cast=lambda v: [s.strip() for s in v.split(',')],
)

# Database - PostgreSQL para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Session configuration - producción
SESSION_COOKIE_SECURE = True  # True en producción con HTTPS

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Agregar apps de Celery para producción
INSTALLED_APPS += [
    'django_celery_beat',
    'django_celery_results',
]

