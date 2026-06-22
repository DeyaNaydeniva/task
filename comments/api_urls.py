from django.urls import path
from .api_views import TaskCommentListView, CommentDetailView

urlpatterns = [
    path('tasks/<int:pk>/comments', TaskCommentListView.as_view()),
    path('comments/<int:pk>', CommentDetailView.as_view()),
]
