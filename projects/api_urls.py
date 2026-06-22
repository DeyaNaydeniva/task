from django.urls import path
from .api_views import ProjectListView, ProjectDetailView, MemberListView, MemberDetailView

urlpatterns = [
    path('projects', ProjectListView.as_view()),
    path('projects/<int:pk>', ProjectDetailView.as_view()),
    path('projects/<int:pk>/members', MemberListView.as_view()),
    path('projects/<int:pk>/members/<int:uid>', MemberDetailView.as_view()),
]
