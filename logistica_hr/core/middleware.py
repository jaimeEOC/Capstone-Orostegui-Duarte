"""
Middleware personalizado para el proyecto Logistica HR
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware para manejar la autenticación y redirección de usuarios
    """

    # URLs que no requieren autenticación
    PUBLIC_URLS = [
        "/",
        "/users/login/",
        "/users/register/",
        "/users/logout/",
        "/access-denied/",
        "/admin/login/",
        "/static/",
        "/media/",
        "/favicon.ico",
    ]

    # URLs que requieren roles específicos
    ROLE_REQUIREMENTS = {
        "/admin/dashboard/": ["admin"],
        "/supervisor/dashboard/": ["admin", "supervisor"],
        "/employee/dashboard/": ["admin", "supervisor", "employee"],
        "/reports/": ["admin", "supervisor"],
        "/performance/": ["admin", "supervisor", "employee"],
        "/employees/": ["admin", "supervisor"],
        "/tasks/": ["admin", "supervisor", "employee"],
    }

    def process_request(self, request):
        """Procesa cada request para verificar autenticación y permisos"""

        # Si es una URL pública, permitir acceso
        if any(request.path.startswith(url) for url in self.PUBLIC_URLS):
            return None

        # Si el usuario no está autenticado, redirigir al login
        if not request.user.is_authenticated:
            messages.warning(
                request, "Debes iniciar sesión para acceder a esta página."
            )
            return redirect(f"{reverse('users:login')}?next={request.path}")

        # Verificar permisos de rol
        if not self._check_role_permissions(request):
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect("access_denied")

        return None

    def _check_role_permissions(self, request):
        """Verifica si el usuario tiene los permisos necesarios para la URL"""
        user_role = request.user.role

        for url_pattern, required_roles in self.ROLE_REQUIREMENTS.items():
            if request.path.startswith(url_pattern):
                return user_role in required_roles

        # Si no hay restricciones específicas, permitir acceso
        return True


class RoleBasedRedirectMiddleware(MiddlewareMixin):
    """
    Middleware para redirigir usuarios según su rol después del login
    """

    def process_response(self, request, response):
        """Procesa la respuesta para redirecciones basadas en rol"""

        # Solo procesar si es una redirección exitosa y el usuario está autenticado
        if (
            response.status_code == 302
            and request.user.is_authenticated
            and "login" in request.path
        ):
            # Obtener la URL de destino
            redirect_url = response.get("Location", "")

            # Si está redirigiendo al dashboard, usar la URL específica del rol
            if "dashboard" in redirect_url:
                role_url = request.user.get_dashboard_url()
                if role_url != redirect_url:
                    response["Location"] = role_url

        return response
