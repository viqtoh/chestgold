

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("signin", login, name="login"),
    path("signup", signup, name="signup"),
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
    path("forgot/password", forgot_password, name="forgot_password"),
    path("resend/confirmation/<str:email>", resend_confirmation, name="resend_confirmation"),
    path("confirm/email/<str:email>", confirm_email, name="confirm_email"),
    path("plans",no_auth_plans, name="no_auth_plans"),
    path("contact", contact, name="contact"),
    path("withdraw", withdraw, name="withdraw"),
    path("plans/subscribe/<str:pid>", subscribe_plan, name="subscribe_plan"),
    path("dasboard/deposit/confirm/deposit", create_trans, name="create_trans"),
]
