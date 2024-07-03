from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from src.core import models


@login_required(login_url='admin:login')
def IndexView(request):
    return HttpResponse('Hi!')
