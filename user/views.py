from django.shortcuts import render, redirect
from. models import User, Address
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.


def index(request):
    return render(request, "index.html")



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
                auth.login(request, user)
                return HttpResponseRedirect(next_url)
            else:
                context["error"] = "Incorrect Email or Password."
        else:
            context["error"] = "Incorrect Email or Password."
    return render(request, 'signin.html', context)

@login_required
def dashboard(request):
    user = request.user
    ref = user.get_ref()
    context ={
        "user": user,
        "ref": ref
    }
    return render(request, "dashboard.html", context)


@login_required
def transactions(request):
    user = request.user
    context ={
        "user": user,
    }
    return render(request, "transactions.html", context)


@login_required
def investments(request):
    user = request.user
    context ={
        "user": user,
    }
    return render(request, "investments.html", context)

@login_required
def plans(request):
    user = request.user
    if(request.method == "POST"):
        return redirect("subscribe")
    context ={
        "user": user,
    }
    return render(request, "plans.html", context)

@login_required
def profile(request):
    user = request.user
    context ={
        "user": user,
    }
    return render(request, "profile.html", context)


@login_required
def change_password(request):
    user = request.user
    context ={
        "user": user,
    }
    return render(request, "change_password.html", context)


@login_required
def subscribe(request):
    user = request.user
    context ={
        "user": user,
    }
    return redirect("insufficient")

@login_required
def insufficient(request):
    user = request.user
    context ={
        "user": user,
    }
    return render(request, "insufficient.html", context)

@login_required
def referrals(request):
    user = request.user
    ref = user.get_ref()
    context ={
        "user": user,
        "ref":ref
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
        "deposit_type": user.dep_type
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
        "amount": user.btc
    }
    return render(request, "bitcoin.html", context)

@login_required
def pay_other(request):
    user = request.user
    context ={
        "user": user,
        "deposit_type": user.dep_type
    }
    return render(request, "deposit_other.html", context)

@login_required
def signout(request):
    auth.logout(request)
    return redirect("index")