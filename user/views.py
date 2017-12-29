from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from app.utils import reverse
from user import forms, models, tokens
from user.forms import SetPasswordForm, PasswordResetForm
from user.models import User
from user.tokens import account_activation_token, password_reset_token


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
                resp = HttpResponseRedirect(next_)
                c_domain = getattr(settings, 'LOGGED_IN_COOKIE_DOMAIN', getattr(settings, 'HACKATHON_DOMAIN', None))
                c_key = getattr(settings, 'LOGGED_IN_COOKIE_KEY', None)
                if c_domain and c_key:
                    try:
                        resp.set_cookie(c_key, 'biene', domain=c_domain, max_age=settings.SESSION_COOKIE_AGE)
                    except:
                        # We don't care if this is not set, we are being cool here!
                        pass
                return resp
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
    resp = HttpResponseRedirect(reverse('account_login'))
    c_domain = getattr(settings, 'LOGGED_IN_COOKIE_DOMAIN', None) or getattr(settings, 'HACKATHON_DOMAIN', None)
    c_key = getattr(settings, 'LOGGED_IN_COOKIE_KEY', None)
    if c_domain and c_key:
        try:
            resp.delete_cookie(c_key, domain=c_domain)
        except:
            # We don't care if this is not deleted, we are being cool here!
            pass
    return resp


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


def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST, )
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            msg = tokens.generate_pw_reset_email(user, request)
            msg.send()
            return HttpResponseRedirect(reverse('password_reset_done'))
        else:
            return TemplateResponse(request, 'password_reset_form.html', {'form': form})
    else:
        form = PasswordResetForm()
    context = {
        'form': form,
    }

    return TemplateResponse(request, 'password_reset_form.html', context)


def password_reset_confirm(request, uid, token):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return TemplateResponse(request, 'password_reset_confirm.html', {'validlink': False})

    if password_reset_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                form.save(user)
                return HttpResponseRedirect(reverse('password_reset_complete'))
        form = SetPasswordForm()
    else:
        return TemplateResponse(request, 'password_reset_confirm.html', {'validlink': False})

    return TemplateResponse(request, 'password_reset_confirm.html', {'validlink': True, 'form': form})


def password_reset_complete(request):
    return TemplateResponse(request, 'password_reset_complete.html', None)


def password_reset_done(request):
    return TemplateResponse(request, 'password_reset_done.html', None)


@login_required
def verify_email_required(request):
    if request.user.email_verified:
        return HttpResponseRedirect(reverse('root'))
    return TemplateResponse(request, 'verify_email_required.html', None)


@login_required
def send_email_verification(request):
    if request.user.email_verified:
        return HttpResponseRedirect(reverse('root'))
    msg = tokens.generate_verify_email(request.user)
    msg.send()
    messages.success(request, "Verification email successfully sent")
    return HttpResponseRedirect(reverse('root'))
