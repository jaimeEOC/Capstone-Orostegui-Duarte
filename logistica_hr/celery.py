"""
Configuración de Celery para el proyecto Logistica HR
"""

import os
from celery import Celery

# Establecer la variable de entorno para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings')

# Crear la instancia de Celery
app = Celery('logistica_hr')

# Usar la configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas automáticamente desde todas las aplicaciones registradas
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Tarea de prueba para verificar que Celery esté funcionando
    """
    print(f'Request: {self.request!r}')


