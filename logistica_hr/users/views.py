"""
Vistas para la aplicación users
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView
from django.urls import reverse
from .forms import RegistrationForm
import json

from .models import User


class LoginView(View):
    """
    Vista para el login de usuarios
    """
    template_name = 'auth/login.html'

    def get(self, request):
        """Muestra el formulario de login"""
        if request.user.is_authenticated:
            return redirect(self.get_redirect_url(request.user))
        return render(request, self.template_name)

    def post(self, request):
        """Procesa el formulario de login"""
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Por favor, completa todos los campos.')
            return render(request, self.template_name)

        # Autenticar usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # ✅ usar siempre auth_login para evitar NameError
                auth_login(request, user)
                messages.success(request, f'¡Bienvenido, {user.full_name}!')

                # Guardar IP de login
                user.last_login_ip = self.get_client_ip(request)
                user.save(update_fields=['last_login_ip'])

                # Redirigir según el rol
                return redirect(self.get_redirect_url(user))
            else:
                messages.error(request, 'Tu cuenta está desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

        return render(request, self.template_name)

    def get_redirect_url(self, user):
        """Retorna la URL de redirección según el rol del usuario"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        if user.is_admin():
            return reverse('admin_dashboard')
        elif user.is_supervisor():
            return reverse('supervisor_dashboard')
        else:
            return reverse('employee_dashboard')

    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def logout_view(request):
    """Vista para cerrar sesión"""
    if request.user.is_authenticated:
        logout(request)
        messages.get_messages(request).used = True
        messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('users:login')


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    return render(request, 'auth/profile.html', {
        'user': request.user
    })


@login_required
def dashboard_redirect(request):
    """Redirecciona al dashboard según el rol del usuario"""
    user = request.user

    if user.is_admin():
        return redirect('admin_dashboard')
    elif user.is_supervisor():
        return redirect('supervisor_dashboard')
    else:
        return redirect('employee_dashboard')


# API Views para autenticación
@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint para login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Usuario y contraseña son requeridos'
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            # ✅ usar auth_login también en la API
            auth_login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login exitoso',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'role_display': user.get_role_display()
                },
                'redirect_url': user.get_dashboard_url()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Credenciales inválidas'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        }, status=400)
    except Exception:
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    """API endpoint para logout"""
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logout exitoso'
    })


@login_required
def api_profile(request):
    """API endpoint para obtener perfil del usuario"""
    user = request.user
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'role': user.role,
            'role_display': user.get_role_display(),
            'phone': user.phone,
            'is_verified': user.is_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat()
        }
    })


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        # Auto-login
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=user.username, password=raw_password)
        if user is not None:
            auth_login(self.request, user)
            messages.success(self.request, "¡Cuenta creada y sesión iniciada!")
            try:
                return redirect(user.get_dashboard_url())
            except Exception:
                return redirect('/')
        messages.success(self.request, "¡Usuario creado! Inicia sesión.")
        return redirect("users:login")
