"""
URLs para la aplicación performance
"""

from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    path('work-log/create/', views.create_work_log, name='create_work_log'),
    path('work-log/<int:log_id>/edit/', views.edit_work_log, name='edit_work_log'),
    path('employee/', views.employee_performance, name='employee_performance'),
]




