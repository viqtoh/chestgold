

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("signin", login, name="login"),
    path("dashboard", dashboard, name="dashboard"),
    path("dashboard/transaction", transactions, name="transactions"),
    path("dashboard/investment", investments, name="investments"),
]
