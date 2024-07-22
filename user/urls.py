

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("signin", login, name="login"),
    path("dashboard", dashboard, name="dashboard"),
    path("dashboard/transaction", transactions, name="transactions"),
    path("dashboard/investment", investments, name="investments"),
    path("dashboard/plans", plans, name="plans"),
    path("dashboard/profile", profile, name="profile"),
    path("dashboard/referrals", referrals, name="referrals"),
    path("dashboard/logout", signout, name="logout"),
    path("dashboard/deposit", deposit, name="deposit"),
    path("dashboard/deposit/amount", deposit_amount, name="deposit_amount"),
    path("dashboard/deposit/btc", pay_btc, name="pay_btc"),
    path("dashboard/deposit/other", pay_other, name="pay_other"),
    path("dashboard/change_password", change_password, name="change_password"),
    path("dashboard/subscribe", subscribe, name="subscribe"),
    path("dashboard/deposit/insufficient", insufficient, name="insufficient"),
]
