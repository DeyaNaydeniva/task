from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:pk>/update/', views.update_task, name='update_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
]
