"""
Vistas de la aplicación core
"""

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


def home(request):
    """
    Vista para la página principal del dashboard
    """
    return render(request, 'home.html')


def employees_list(request):
    """
    Vista para la lista de empleados
    """
    return render(request, 'employees_list.html')


def tasks_list(request):
    """
    Vista para la lista de tareas
    """
    return render(request, 'tasks_list.html')


def performance_dashboard(request):
    """
    Vista para el dashboard de rendimiento
    """
    return render(request, 'performance_dashboard.html')


def reports_list(request):
    """
    Vista para la lista de reportes
    """
    return render(request, 'reports_list.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Endpoint raíz de la API que muestra todos los endpoints disponibles
    """
    return Response({
        'message': 'Logistica HR API - Configuración Mínima',
        'status': 'active',
        'available_endpoints': [
            'health/',
            'admin/',
        ],
        'note': 'Otras aplicaciones están temporalmente deshabilitadas para desarrollo'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint para verificar el estado de salud de la aplicación
    """
    return Response({
        'status': 'healthy',
        'message': 'Logistica HR API está funcionando correctamente'
    })

