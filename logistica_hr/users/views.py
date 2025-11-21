"""
Vistas para la aplicación users
"""

import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView

from .forms import RegistrationForm

User = get_user_model()

class LoginView(View):
    """
    Vista para el login de usuarios
    """

    template_name = "auth/login.html"

    def get(self, request):
        """Muestra el formulario de login"""
        if request.user.is_authenticated:
            return redirect(self.get_redirect_url(request.user))

        context = {
            'show_session_warning': True,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Procesa el formulario de login (por correo)"""
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Por favor, completa todos los campos.")
            context = {'show_session_warning': True}
            return render(request, self.template_name, context)

        user = None

        try:
            # Buscar usuario por correo (case-insensitive)
            user_obj = User.objects.get(email__iexact=email)

            # Autenticar usando el USERNAME interno
            user = authenticate(
                request,
                username=user_obj.username,
                password=password,
            )
        except User.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {user.full_name}!")

                # Guardar IP de login
                user.last_login_ip = self.get_client_ip(request)
                user.save(update_fields=["last_login_ip"])

                # Redirigir según el rol
                return redirect(self.get_redirect_url(user))
            else:
                messages.error(request, "Tu cuenta está desactivada.")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")

        context = {'show_session_warning': True}
        return render(request, self.template_name, context)


    def get_redirect_url(self, user):
        """Retorna la URL de redirección según el rol del usuario"""
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url

        if user.is_admin():
            return reverse("admin_dashboard")
        elif user.is_supervisor():
            return reverse("supervisor_dashboard")
        else:
            return reverse("employee_dashboard")

    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


def logout_view(request):
    """Vista para cerrar sesión"""
    if request.user.is_authenticated:
        logout(request)
        messages.get_messages(request).used = True
        messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("users:login")


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    return render(request, "auth/profile.html", {"user": request.user})


@login_required
def dashboard_redirect(request):
    """Redirecciona al dashboard según el rol del usuario"""
    user = request.user

    if user.is_admin():
        return redirect("admin_dashboard")
    elif user.is_supervisor():
        return redirect("supervisor_dashboard")
    else:
        return redirect("employee_dashboard")


# API Views para autenticación
@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint para login"""
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse(
                {"success": False, "message": "Usuario y contraseña son requeridos"},
                status=400,
            )

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Login exitoso",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "role_display": user.get_role_display(),
                    },
                    "redirect_url": user.get_dashboard_url(),
                }
            )
        else:
            return JsonResponse(
                {"success": False, "message": "Credenciales inválidas"}, status=401
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Datos JSON inválidos"}, status=400
        )
    except Exception:
        return JsonResponse(
            {"success": False, "message": "Error interno del servidor"}, status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    """API endpoint para logout"""
    logout(request)
    return JsonResponse({"success": True, "message": "Logout exitoso"})


@login_required
def api_profile(request):
    """API endpoint para obtener perfil del usuario"""
    user = request.user
    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "role": user.role,
                "role_display": user.get_role_display(),
                "phone": user.phone,
                "is_verified": user.is_verified,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "date_joined": user.date_joined.isoformat(),
            },
        }
    )


class RegisterView(FormView):
    """
    Vista para el registro de usuarios
    """

    template_name = "auth/register.html"
    form_class = RegistrationForm
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        """Redirigir si ya está autenticado"""
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Procesar formulario válido"""
        # Aquí NO usamos try/except que silencie errores
        user = form.save()

        raw_password = form.cleaned_data.get("password1")

        user = authenticate(
            self.request,
            username=user.username,
            password=raw_password
        )

        if user:
            login(self.request, user)

            # borrar mensajes arrastrados
            messages.get_messages(self.request).used = True

            return redirect(self.get_success_url())

        # Si por alguna razón no se pudo autenticar:
        messages.get_messages(self.request).used = True
        return redirect("users:login")


    def get_success_url(self):
        """Obtener URL de redirección después del registro exitoso"""
        if self.request.user.is_authenticated:
            try:
                return self.request.user.get_dashboard_url()
            except Exception:
                return "/"
        return "/"
