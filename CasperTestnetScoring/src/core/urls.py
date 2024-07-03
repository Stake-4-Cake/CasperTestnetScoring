from django.urls import path, include

from src.core import views


urlpatterns = [
    path('', views.IndexView, name='index')
]
