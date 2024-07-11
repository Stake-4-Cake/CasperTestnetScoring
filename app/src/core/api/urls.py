from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from src.core.api import views


urlpatterns = [
    path('scoring/quarters', views.get_quarters_view, name='quarters'),
    path('scoring/weeks/<str:quarter>', views.get_weeks_view, name='weeks'),
    path('scoring/days/<str:week>', views.get_days_view, name='days'),
    path('scoring/intervals/<str:day>', views.get_intervals_view, name='intervals')
]

urlpatterns = format_suffix_patterns(urlpatterns)
