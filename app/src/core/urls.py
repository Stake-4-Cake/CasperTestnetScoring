from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('api/v1/', include('src.core.api.urls'))
]
