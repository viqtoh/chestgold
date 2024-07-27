from django.shortcuts import render, redirect
from. models import User, Address
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from datetime import datetime, timedelta, date
from django.conf import settings


# Create your views here.


def index(request):
    return render(request, "index.html")

def no_auth_plans(request):
    return render(request, "no_auth_plan.html")

def contact(request):
    return render(request, "contact.html")



def login(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        next_url = request.POST.get('next')
        context["email"]=email
        if(not next_url):
            next_url =reverse('dashboard')
        context['next'] = next_url
        if user:
            if user.check_password(password):
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(next_url)
                else:
                    url = reverse("resend_confirmation", args=[email])
                    return redirect(url)
            else:
                context["error"] = "Incorrect Email or Password."
        else:
            context["error"] = "Incorrect Email or Password."
    return render(request, 'signin.html', context)


def signup(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
        user = User.objects.filter(email=email).first()
        if(user):
            return render(request, 'signup.html', {"error": "Email already exists"})
        nwuser = User(email=email, first_name=first_name, last_name=last_name, is_active=False, phone=phone)
        nwuser.save()
        nwuser.set_password(password)
        random_numbers = [random.randint(0, 9) for _ in range(6)]
        otp = ''.join(map(str, random_numbers))
        nwuser.email_confirmation_code= otp
        nwuser.otpt=timezone.now()
        nwuser.save()
        url = reverse("confirm_email", args=[email])
        html_message = render_to_string('confirm_template.html', {'otp':otp, "name": nwuser.get_name(), "domain": request.get_host(),"url":url })
        plain_message = strip_tags(html_message)
        mail.send_mail('Verify Email Address', plain_message, settings.EMAIL_HOST_USER, [email], html_message=html_message)
        return redirect(url)
    return render(request, 'signup.html', context)


def resend_confirmation(request,email):
    context = {}
    user = User.objects.filter(email=email).first()
    if(not user):
        return render(request, 'signup.html', {"error": "Email not registered"})
    random_numbers = [random.randint(0, 9) for _ in range(6)]
    otp = ''.join(map(str, random_numbers))
    user.email_confirmation_code= otp
    user.otpt=timezone.now()
    user.save()
    url = reverse("confirm_email", args=[email])
    html_message = render_to_string('confirm_template.html', {'otp':otp, "name": user.get_name(), "domain": request.get_host(),"url":url })
    plain_message = strip_tags(html_message)
    mail.send_mail('Verify Email Address', plain_message, settings.EMAIL_HOST_USER, [email], html_message=html_message)
    return redirect(url)



def forgot_password(request):
    context = {}
    if(request.method == "POST"):
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if(not user):
            return render(request, 'signup.html', {"error": "Email not registered"})
        random_numbers = [random.randint(0, 9) for _ in range(6)]
        otp = ''.join(map(str, random_numbers))
        user.email_confirmation_code= otp
        user.otpt=timezone.now()
        user.save()
        html_message = render_to_string('confirm_template.html', {'otp':otp, "name": user.get_name() })
        plain_message = strip_tags(html_message)
        mail.send_mail('Verify Email Address', plain_message, settings.SMTP_FROM, [email], html_message=html_message)
        url = reverse("confirm_email", args=[email])
        return redirect(url)
    return render(request, "forgot_password.html", context)


def confirm_email(request,email):
    context = {"email":email}
    if request.method == "POST":
        code = request.POST.get("code")
        user = User.objects.filter(email=email).first()
        if(user):
            if(user.email_confirmation_code == code):
                time_difference = abs(user.otpt - timezone.now())
                if time_difference > timedelta(minutes=15):
                    context["error"] = "Code Expired"
                    return render(request, "confirm_email.html", context)
                user.is_active = True
                user.save()
                return redirect("login")
            else:
                context["error"] = "Invalid Code"
        else:
            return redirect("signup")
    return render(request, 'confirm_email.html', context)

@login_required
def dashboard(request):
    user:User = request.user
    ref = user.get_ref()
    
    context ={
        "user": user,
        "ref": ref,
        "balance": user.get_balance(),
        "total_withdrawn": user.get_total_withdrawal(),
        "total_withdrawn_m": user.get_total_withdrawal_this_month(),
        "total_deposited": user.get_total_deposit(),
        "total_deposited_m": user.get_total_deposit_this_month(),
        "inv_acc": 0
    }
    return render(request, "dashboard.html", context)


@login_required
def transactions(request):
    user = request.user
    transactions = user.transactions.all()

    context ={
        "user": user,
        "transactions":transactions,
    }
    return render(request, "transactions.html", context)


@login_required
def investments(request):
    user = request.user
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "investments.html", context)

@login_required
def plans(request):
    user = request.user
    if(request.method == "POST"):
        return redirect("subscribe")
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "plans.html", context)

@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        next_of_kin= request.POST.get("next_of_kin")
        next_of_kin_phone= request.POST.get("next_of_kin_phone")
        country = request.POST.get("country")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.next_of_kin = next_of_kin
        user.next_of_kin_phone = next_of_kin_phone
        user.country = country
        user.address = address
        user.gender = gender
        user.save()
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "profile.html", context)


@login_required
def change_password(request):
    user = request.user
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "change_password.html", context)


@login_required
def subscribe(request):
    user = request.user
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return redirect("insufficient")

@login_required
def insufficient(request):
    user = request.user
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "insufficient.html", context)

@login_required
def referrals(request):
    user = request.user
    ref = user.get_ref()
    context ={
        "user": user,
        "ref":ref,
        "balance": user.get_balance(),
    }
    return render(request, "referrals.html", context)

@login_required
def deposit(request):
    user = request.user
    if(request.method == "POST"):
        user.dep_type =request.POST.get("deposit")
        user.save()
        return redirect("deposit_amount")
    context ={
        "user": user,
        "balance": user.get_balance(),
    }
    return render(request, "deposit.html", context)

@login_required
def deposit_amount(request):
    user = request.user
    if(request.method =="POST"):
        user.usd = float(request.POST.get("usd_amount"))
        btc = request.POST.get("btc_amount")
        btc=btc.split(" BTC")[0]
        user.btc = float(btc)
        user.save()
        if(user.dep_type == "btc"):
            return redirect("pay_btc")
        else:
            return redirect("pay_other")
    context ={
        "user": user,
        "deposit_type": user.dep_type,
        "balance": user.get_balance(),
    }
    return render(request, "deposit_amount.html", context)

@login_required
def pay_btc(request):
    user = request.user
    address = Address.objects.filter(active=True).first()
    if(not address):
        return render(request, "bitcoin.html", {"err":"this method is currently unavailable"})
    context ={
        "user": user,
        "deposit_type": user.dep_type,
        "address": address,
        "amount": user.btc,
        "balance": user.get_balance(),
    }
    return render(request, "bitcoin.html", context)

@login_required
def pay_other(request):
    user = request.user
    context ={
        "user": user,
        "deposit_type": user.dep_type,
        "balance": user.get_balance(),
    }
    return render(request, "deposit_other.html", context)

@login_required
def signout(request):
    auth.logout(request)
    return redirect("index")