from django.shortcuts import render, redirect
from. models import User
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
    context ={
        "user": request.user
    }
    return render(request, "dashboard.html", context)