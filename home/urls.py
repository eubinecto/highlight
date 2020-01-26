from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.get_url, name='get_url'),
]
