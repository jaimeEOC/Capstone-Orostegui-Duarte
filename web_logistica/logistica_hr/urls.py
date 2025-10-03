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
    
    # APIs (comentadas temporalmente hasta implementar)
    # path('api/v1/employees/', include('logistica_hr.employees.urls')),
    # path('api/v1/tasks/', include('logistica_hr.tasks.urls')),
    # path('api/v1/performance/', include('logistica_hr.performance.urls')),
    # path('api/v1/reports/', include('logistica_hr.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
