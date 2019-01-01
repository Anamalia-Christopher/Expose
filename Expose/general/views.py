from django.shortcuts import render,reverse
from django.http import HttpResponseRedirect
from .controller import *

from django.contrib.auth import login
from django.contrib.auth.models import User

# Create your views here.



def Home(reqeust):
    return render(reqeust, 'general/home.html')

def Login(request):
    if request.method == 'POST':
        logged_in = Login_C(request=request).Login()
        if logged_in:
            return HttpResponseRedirect(reverse('career', args=(logged_in, )))

        return render(request, 'general/login.html', {'error': "Incorrect login credentials"})

    return render(request, 'general/login.html')


def Register(request):

    if request.method == 'POST':
        registration = Registration(request.POST)

        registration.Emailing()

        id = registration.__str__()
        print(id)

        del registration
        return HttpResponseRedirect(reverse('confirmation', args=(id,)))
    return render(request, 'general/register.html')

def About(request):

    return render(request, 'general/about.html')

def Logout(request):

    Logout_C(request=request)
    return HttpResponseRedirect(reverse('login'))

def ForgetPassword(request):
    if request.method == 'POST':
        ForgetPassword_controller(email=request.POST.get('email')).SendMail()

        return HttpResponseRedirect(reverse('LinkSuccess'))

    return render(request, 'general/forget.html')

# todo - that you cant confirm you account more than once
def RegisterConfirmation(request, id):
    print(id)
    if request.method == 'POST':
        confirmation= Confirmation(POST=request.POST, id=id)

        if confirmation.Confirm():
            confirmation.Login(request=request)

        else:
            return render(request, 'general/confirmation.html', {'id': id, 'error':"Incorrect Confirmation code"})

            # return HttpResponseRedirect(reverse('confirmation', args=(id, )))

    return render(request, 'general/confirmation.html', {'id':id})


def ResetPassword(request, id):
    reset = Reset_controller(id=id)

    if not reset.id_checker():
        print(reset.id_checker())
        return HttpResponseRedirect(reverse('404'))

    if request.method == 'POST':
        reset.SetPassword(request.POST)

        return HttpResponseRedirect(reverse('Success'))
    return render(request, 'general/reset.html',{'id':id})


def FOF(request):
    return render(request, 'general/404.html')


def ResetSuccess(request):
    return render(request, 'general/successReset.html')


def Career(request, id):
    if request.method == 'POST':
        Career_C(id=id).SaveChanges(POST=request.POST)
    Career_C(id).GatherAll()
    return render(request, 'general/career.html', {'id':id})



# This is to send a successful sending of reset password email
def SuccessRequest(request):
    return render(request, 'general/success.html')

def Del(request):
    return render(request, 'general/del.html')