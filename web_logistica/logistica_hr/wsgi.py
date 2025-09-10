"""
WSGI config for logistica_hr project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings')

application = get_wsgi_application()

