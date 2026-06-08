from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:pk>/update/', views.update_task, name='update_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:pk>/labels/<int:label_pk>/', views.toggle_task_label, name='toggle_task_label'),
    path('projects/<int:pk>/labels/', views.create_label, name='create_label'),
    path('labels/<int:pk>/delete/', views.delete_label, name='delete_label'),
]
