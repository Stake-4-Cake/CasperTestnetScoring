from django.urls import path, include


urlpatterns = [
    path('api/v1/', include('src.core.api.urls'))
]
