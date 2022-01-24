from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone

from user.models import LoginRequest

import requests


def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            if not settings.GOOGLE_RECAPTCHA_SECRET_KEY:
                request.recaptcha_is_valid = True
            else:
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                if result['success']:
                    request.recaptcha_is_valid = True
                else:
                    request.recaptcha_is_valid = False
                    messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def reset_tries(request):
    client_ip = get_client_ip(request)
    login_request = LoginRequest.objects.get(ip=client_ip)
    login_request.reset_tries()
    login_request.save()


def check_client_ip(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        aux = None
        if len(args) > 0 and isinstance(args[0], WSGIRequest):
            aux = request
            request = args[0]
        request.client_req_is_valid = None
        if request.method == 'POST':
            client_ip = get_client_ip(request)
            request_time = timezone.now()
            print(request_time)
            try:
                login_request = LoginRequest.objects.get(ip=client_ip)
                latest_request = login_request.get_latest_request()
                if request_time - latest_request < timedelta(minutes=5):
                    login_request.increment_tries()
                else:
                    login_request.reset_tries()
                if login_request.login_tries < 4:
                    login_request.set_latest_request(request_time)
                    login_request.save()
            except LoginRequest.DoesNotExist:
                login_request = LoginRequest.objects.create(ip=client_ip, latestRequest=request_time)
                login_request.save()
            if login_request.login_tries < 4:
                request.client_req_is_valid = True
            else:
                request.client_req_is_valid = False
            if aux:
                request = aux
        return view_func(request, *args, **kwargs)

    return _wrapped_view
