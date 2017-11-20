from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from app.utils import reverse
from user import forms, models
from user.models import User
from user.tokens import account_activation_token


def login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        next_ = request.GET.get('next', '/')
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(email=email, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next_)
            else:
                form.add_error(None, 'Wrong Username or Password. Please try again.')

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
            name = form.cleaned_data['name']

            if models.User.objects.filter(email=email).first() is not None:
                messages.error(request, 'An account with this email already exists')
            else:
                user = models.User.objects.create_user(email=email, password=password, name=name)
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


def activate(request, uid, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
        if request.user != user:
            messages.warning(request, "User email can be verified")
            return redirect('root')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.warning(request, "User email can be verified")
        return redirect('root')

    if account_activation_token.check_token(user, token):
        messages.success(request, "Email verified!")

        user.email_verified = True
        user.save()
        auth.login(request, user)
    else:
        messages.error(request, "This email verification url has expired")
    return redirect('root')
