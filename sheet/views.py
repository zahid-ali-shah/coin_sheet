# from django.http import Http404
from django.shortcuts import render


def home(request):
    # raise Http404("Poll does not exist")
    return render(request, "sheet/home.html")
