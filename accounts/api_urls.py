from django.urls import path
from .api_views import SignUpView, SignInView, LogoutView

urlpatterns = [
    path('sign-up', SignUpView.as_view()),
    path('sign-in', SignInView.as_view()),
    path('logout', LogoutView.as_view()),
]
