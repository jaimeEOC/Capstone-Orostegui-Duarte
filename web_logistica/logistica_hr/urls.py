"""
URLs principales del proyecto Logistica HR
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('logistica_hr.core.urls')),  # Página principal y navegación
    path('admin/', admin.site.urls),
    # path('api/v1/users/', include('logistica_hr.users.urls')),          # Comentado temporalmente
    # path('api/v1/employees/', include('logistica_hr.employees.urls')),  # Comentado temporalmente
    # path('api/v1/tasks/', include('logistica_hr.tasks.urls')),          # Comentado temporalmente
    # path('api/v1/performance/', include('logistica_hr.performance.urls')), # Comentado temporalmente
    # path('api/v1/reports/', include('logistica_hr.reports.urls')),      # Comentado temporalmente
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
