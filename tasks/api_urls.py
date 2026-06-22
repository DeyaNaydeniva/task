from django.urls import path
from .api_views import (
    ProjectTaskListView, TaskDetailView,
    ProjectLabelListView, LabelDetailView,
)

urlpatterns = [
    path('projects/<int:pk>/tasks', ProjectTaskListView.as_view()),
    path('tasks/<int:pk>', TaskDetailView.as_view()),
    path('projects/<int:pk>/labels', ProjectLabelListView.as_view()),
    path('labels/<int:pk>', LabelDetailView.as_view()),
]
