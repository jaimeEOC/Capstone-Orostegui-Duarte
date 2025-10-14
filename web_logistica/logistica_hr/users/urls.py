"""
URLs para la aplicación users
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "users"

router = DefaultRouter()
# router.register(r'', views.UserViewSet)  # Comentado hasta crear las vistas

urlpatterns = [
    # Vistas de autenticación
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    # API endpoints
    path("api/login/", views.api_login, name="api_login"),
    path("api/logout/", views.api_logout, name="api_logout"),
    path("api/profile/", views.api_profile, name="api_profile"),
    # Incluir URLs del router
    path("", include(router.urls)),
]
