from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'app_users'
urlpatterns = [
    path('signin/', LoginView.as_view(template_name='app_users/signin.html'), name='signin'),
]
