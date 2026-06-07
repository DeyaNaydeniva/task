from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/tasks/add/', views.add_task, name='add_task'),
]
