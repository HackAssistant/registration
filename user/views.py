from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.utils import reverse
from user import forms, models


def login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        next_ = request.GET.get('next', '/')
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(email=email, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next_)
            else:
                messages.error(request, 'There\'s no such a user. Sign up if you haven\'t yet created an account')

    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form})


def signup(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            nickname = form.cleaned_data['nickname']

            if models.User.objects.filter(email=email).first() is not None:
                messages.error(request, 'An account with this email already exists')
            else:
                user = models.User.objects.create_user(email=email, password=password, nickname=nickname)
                user = auth.authenticate(email=email, password=password)
                auth.login(request, user)
                return HttpResponseRedirect(reverse('root'))
    else:
        form = forms.RegisterForm()

    return render(request, 'signup.html', {'form': form})


def logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully logged out!')
    return HttpResponseRedirect(reverse('account_login'))
