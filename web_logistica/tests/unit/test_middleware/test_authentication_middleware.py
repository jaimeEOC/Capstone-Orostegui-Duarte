"""
Pruebas unitarias para el middleware de autenticación
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthMiddleware
from django.urls import reverse
from unittest.mock import Mock

from logistica_hr.core.middleware import AuthenticationMiddleware, RoleBasedRedirectMiddleware
from tests.factories import AdminUserFactory, SupervisorUserFactory, EmployeeUserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.middleware
class TestAuthenticationMiddleware:
    """Pruebas para el middleware de autenticación"""

    def setup_method(self):
        """Configuración inicial para cada prueba"""
        self.factory = RequestFactory()
        # Crear middleware con get_response mock
        self.middleware = AuthenticationMiddleware(lambda req: None)
        self.admin_user = AdminUserFactory()
        self.supervisor_user = SupervisorUserFactory()
        self.employee_user = EmployeeUserFactory()

    def _add_session_middleware(self, request):
        """Agregar middleware de sesión para testing"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Agregar middleware de mensajes
        from django.contrib.messages.middleware import MessageMiddleware
        msg_middleware = MessageMiddleware(lambda req: None)
        msg_middleware.process_request(request)
        
        return request

    def _add_auth_middleware(self, request):
        """Agregar middleware de autenticación de Django"""
        middleware = DjangoAuthMiddleware(lambda req: None)
        middleware.process_request(request)
        return request

    def test_public_urls_allow_access_without_auth(self):
        """Probar que las URLs públicas permiten acceso sin autenticación"""
        public_urls = [
            '/users/login/',
            '/users/logout/',
            '/access-denied/',
            '/admin/login/',
            '/static/css/style.css',
            '/media/avatars/user.jpg',
            '/favicon.ico'
        ]
        
        for url in public_urls:
            request = self.factory.get(url)
            request.user = None
            response = self.middleware.process_request(request)
            assert response is None, f"URL {url} debería permitir acceso sin autenticación"

    def test_private_urls_require_authentication(self):
        """Probar que las URLs privadas requieren autenticación"""
        private_urls = [
            '/admin/dashboard/',
            '/supervisor/dashboard/',
            '/employee/dashboard/',
            '/reports/',
            '/performance/',
            '/employees/',
            '/tasks/'
        ]
        
        for url in private_urls:
            request = self.factory.get(url)
            # Crear un mock de usuario no autenticado
            request.user = Mock()
            request.user.is_authenticated = False
            # Agregar middleware de mensajes
            self._add_session_middleware(request)
            response = self.middleware.process_request(request)
            assert response is not None, f"URL {url} debería requerir autenticación"
            assert response.status_code == 302, f"URL {url} debería redirigir al login"

    def test_authenticated_user_can_access_private_urls(self):
        """Probar que usuarios autenticados pueden acceder a URLs privadas"""
        private_urls = [
            '/admin/dashboard/',
            '/supervisor/dashboard/',
            '/employee/dashboard/',
            '/reports/',
            '/performance/',
            '/employees/',
            '/tasks/'
        ]
        
        for url in private_urls:
            request = self.factory.get(url)
            request.user = self.admin_user
            response = self.middleware.process_request(request)
            assert response is None, f"Admin debería poder acceder a {url}"

    def test_admin_can_access_admin_dashboard(self):
        """Probar que admin puede acceder al dashboard de admin"""
        request = self.factory.get('/admin/dashboard/')
        request.user = self.admin_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_supervisor_can_access_supervisor_dashboard(self):
        """Probar que supervisor puede acceder al dashboard de supervisor"""
        request = self.factory.get('/supervisor/dashboard/')
        request.user = self.supervisor_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_can_access_employee_dashboard(self):
        """Probar que empleado puede acceder al dashboard de empleado"""
        request = self.factory.get('/employee/dashboard/')
        request.user = self.employee_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_cannot_access_admin_dashboard(self):
        """Probar que empleado no puede acceder al dashboard de admin"""
        request = self.factory.get('/admin/dashboard/')
        request.user = self.employee_user
        # Mock del sistema de mensajes
        request._messages = Mock()
        response = self.middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == reverse('access_denied')

    def test_supervisor_cannot_access_admin_dashboard(self):
        """Probar que supervisor no puede acceder al dashboard de admin"""
        request = self.factory.get('/admin/dashboard/')
        request.user = self.supervisor_user
        # Mock del sistema de mensajes
        request._messages = Mock()
        response = self.middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == reverse('access_denied')

    def test_admin_can_access_supervisor_dashboard(self):
        """Probar que admin puede acceder al dashboard de supervisor"""
        request = self.factory.get('/supervisor/dashboard/')
        request.user = self.admin_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_admin_can_access_employee_dashboard(self):
        """Probar que admin puede acceder al dashboard de empleado"""
        request = self.factory.get('/employee/dashboard/')
        request.user = self.admin_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_supervisor_can_access_employee_dashboard(self):
        """Probar que supervisor puede acceder al dashboard de empleado"""
        request = self.factory.get('/employee/dashboard/')
        request.user = self.supervisor_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_cannot_access_reports(self):
        """Probar que empleado no puede acceder a reportes"""
        request = self.factory.get('/reports/')
        request.user = self.employee_user
        # Mock del sistema de mensajes
        request._messages = Mock()
        response = self.middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == reverse('access_denied')

    def test_supervisor_can_access_reports(self):
        """Probar que supervisor puede acceder a reportes"""
        request = self.factory.get('/reports/')
        request.user = self.supervisor_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_admin_can_access_reports(self):
        """Probar que admin puede acceder a reportes"""
        request = self.factory.get('/reports/')
        request.user = self.admin_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_can_access_performance(self):
        """Probar que empleado puede acceder a performance"""
        request = self.factory.get('/performance/')
        request.user = self.employee_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_can_access_tasks(self):
        """Probar que empleado puede acceder a tareas"""
        request = self.factory.get('/tasks/')
        request.user = self.employee_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_employee_cannot_access_employees_list(self):
        """Probar que empleado no puede acceder a lista de empleados"""
        request = self.factory.get('/employees/')
        request.user = self.employee_user
        # Mock del sistema de mensajes
        request._messages = Mock()
        response = self.middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == reverse('access_denied')

    def test_supervisor_can_access_employees_list(self):
        """Probar que supervisor puede acceder a lista de empleados"""
        request = self.factory.get('/employees/')
        request.user = self.supervisor_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_redirect_includes_next_parameter(self):
        """Probar que la redirección incluye el parámetro next"""
        request = self.factory.get('/admin/dashboard/')
        # Crear un mock de usuario no autenticado
        request.user = Mock()
        request.user.is_authenticated = False
        self._add_session_middleware(request)
        response = self.middleware.process_request(request)
        assert response is not None
        assert 'next=' in response.url
        assert '/admin/dashboard/' in response.url

    def test_unknown_url_allows_access(self):
        """Probar que URLs desconocidas permiten acceso si no hay restricciones"""
        request = self.factory.get('/unknown/url/')
        request.user = self.employee_user
        response = self.middleware.process_request(request)
        assert response is None

    def test_url_pattern_matching(self):
        """Probar que el matching de patrones de URL funciona correctamente"""
        # URLs que empiezan con el patrón
        request = self.factory.get('/admin/dashboard/some/sub/path/')
        request.user = self.employee_user
        # Mock del sistema de mensajes
        request._messages = Mock()
        response = self.middleware.process_request(request)
        assert response is not None
        assert response.url == reverse('access_denied')

        # URLs que no empiezan con el patrón
        request = self.factory.get('/admin-other/')
        request.user = self.employee_user
        response = self.middleware.process_request(request)
        assert response is None


@pytest.mark.django_db
@pytest.mark.middleware
class TestRoleBasedRedirectMiddleware:
    """Pruebas para el middleware de redirección basada en roles"""

    def setup_method(self):
        """Configuración inicial para cada prueba"""
        self.middleware = RoleBasedRedirectMiddleware(lambda req: None)
        self.admin_user = AdminUserFactory()
        self.supervisor_user = SupervisorUserFactory()
        self.employee_user = EmployeeUserFactory()

    def test_redirect_after_login_admin(self):
        """Probar redirección después del login para admin"""
        request = Mock()
        request.path = '/users/login/'
        request.user = self.admin_user
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que se actualizó la URL de redirección
        response.__setitem__.assert_called_with('Location', '/admin/dashboard/')

    def test_redirect_after_login_supervisor(self):
        """Probar redirección después del login para supervisor"""
        request = Mock()
        request.path = '/users/login/'
        request.user = self.supervisor_user
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que se actualizó la URL de redirección
        response.__setitem__.assert_called_with('Location', '/supervisor/dashboard/')

    def test_redirect_after_login_employee(self):
        """Probar redirección después del login para empleado"""
        request = Mock()
        request.path = '/users/login/'
        request.user = self.employee_user
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que se actualizó la URL de redirección
        response.__setitem__.assert_called_with('Location', '/employee/dashboard/')

    def test_no_redirect_for_non_login_path(self):
        """Probar que no hay redirección para rutas que no son login"""
        request = Mock()
        request.path = '/other/path/'
        request.user = self.admin_user
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que no se modificó la respuesta
        response.__setitem__.assert_not_called()

    def test_no_redirect_for_non_302_response(self):
        """Probar que no hay redirección para respuestas que no son 302"""
        request = Mock()
        request.path = '/users/login/'
        request.user = self.admin_user
        
        response = Mock()
        response.status_code = 200
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que no se modificó la respuesta
        response.__setitem__.assert_not_called()

    def test_no_redirect_for_unauthenticated_user(self):
        """Probar que no hay redirección para usuarios no autenticados"""
        request = Mock()
        request.path = '/users/login/'
        # Crear un mock de usuario no autenticado
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que no se modificó la respuesta
        response.__setitem__.assert_not_called()

    def test_no_redirect_when_dashboard_url_matches(self):
        """Probar que no hay redirección cuando la URL ya es la correcta"""
        request = Mock()
        request.path = '/users/login/'
        request.user = self.admin_user
        
        response = Mock()
        response.status_code = 302
        response.get.return_value = '/admin/dashboard/'
        response.__setitem__ = Mock()
        
        result = self.middleware.process_response(request, response)
        
        # Verificar que no se modificó la respuesta
        response.__setitem__.assert_not_called()
