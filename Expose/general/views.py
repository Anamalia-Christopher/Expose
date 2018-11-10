from django.shortcuts import render,reverse
from django.http import HttpResponseRedirect

# Create your views here.

def Home(reqeust):
    return render(reqeust, 'general/home.html')

def Login(request):
    return render(request, 'general/login.html')


def Register(request):
    return render(request, 'general/register.html')

def About(request):
    return render(request, 'general/about.html')

def Logout(request):
    return HttpResponseRedirect(reverse('login'))

def ForgetPassword(request):
    pass

def RegisterConfirmation(request):
    pass