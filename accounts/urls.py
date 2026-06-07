from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.auth_page, name='auth'),
    path('signin/', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),
]
