import datetime

from django.http import HttpResponse
from django.shortcuts import render


def time(request):
    return HttpResponse(f"Time = {datetime.datetime.now().time()}")

# Create your views here.
