from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('mine/', views.my_tasks, name='my_tasks'),
    path('', views.my_tasks, name='index'),
    path('create/', views.create_task, name='create_task'),
    path('api/<int:task_id>/<str:new_status>/', views.update_task_status_api, name='update_task_status_api'),
]
