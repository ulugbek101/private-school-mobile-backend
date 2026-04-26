from django.urls import path

from app_main import views


app_name = 'app_main'
urlpatterns = [
    path('', views.index, name='index'),
]
