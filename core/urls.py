from django.contrib import admin
from django.urls import path

from .views import HomeView, BankView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('bank', BankView.as_view(), name="bank"),
]
