from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from src.core.api import views


urlpatterns = [
    path('scoring/quarters', views.get_quarters, name='quarters'),
    path('scoring/weeks/<str:quarter>', views.get_weeks, name='weeks'),
    path('scoring/days/<str:week>', views.get_days, name='days'),
    path('scoring/intervals/<str:day>', views.get_intervals, name='intervals'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
