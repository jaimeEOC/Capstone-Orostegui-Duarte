"""
URLs principales del proyecto Logistica HR
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Autenticación
    path('users/', include('logistica_hr.users.urls')),
    
    # Páginas principales
    path('', include('logistica_hr.core.urls')),
    
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Tareas
    path('tasks/', include('logistica_hr.tasks.urls')),
    
    # Performance
    path('performance/', include('logistica_hr.performance.urls')),
    
    # APIs (comentadas temporalmente hasta implementar)
    # path('api/v1/employees/', include('logistica_hr.employees.urls')),
    # path('api/v1/reports/', include('logistica_hr.reports.urls')),
]

if settings.DEBUG:
    # Servir archivos de media en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Los archivos estáticos se sirven automáticamente por django.contrib.staticfiles
    # cuando DEBUG=True, desde STATICFILES_DIRS
