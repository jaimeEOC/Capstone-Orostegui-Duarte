"""
URLs para la aplicación users
"""

from django.urls import path
from . import views
from .views import RegisterView

app_name = 'users'

urlpatterns = [
    # Vistas de autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # API endpoints
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/profile/', views.api_profile, name='api_profile'),
]
