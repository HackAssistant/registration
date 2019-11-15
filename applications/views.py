# Create your views here.
from __future__ import print_function

import os
from django.conf import settings
import zipfile
import io

import logging
from datetime import timedelta
import random

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from app import slack
from app.slack import SlackInvitationException
from app.utils import reverse, hacker_tabs
from app.views import TabsView
from applications import models, emails, forms


def check_application_exists(user, uuid):
    try:
        application = models.Application.objects.get(user=user)
    except models.Application.DoesNotExist:
        raise Http404
    if not application or uuid != application.uuid_str:
        raise Http404


def new_secret_code():
    temp_code = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

    try:
        models.Ambassador.objects.get(secret_code=temp_code)
    except(models.Ambassador.DoesNotExist):
        return temp_code
    else:
        return new_secret_code()


def zipCVs(request):
    if not request.user.is_staff:
        return Http404

    apps = models.Application.objects.filter(
        status__in=[models.APP_ATTENDED, models.APP_CONFIRMED]
    )

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for app in apps:
            backup_zip.write(os.path.join(settings.MEDIA_ROOT, str(app.resume)))

    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=' + 'resumes.zip'
    response['Content-Length'] = zip_io.tell()
    return response


def texCVs(request):
    if not request.user.is_staff:
        return Http404

    apps = models.Application.objects.filter(
        status__in=[models.APP_ATTENDED, models.APP_CONFIRMED]
    )

    return render(request, 'cv_template.html', context={'applications': apps})


class ConfirmApplication(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get(self, request, *args, **kwargs):
        application = models.Application.objects.get(user=request.user)
        msg = None
        if application.can_confirm():
            msg = emails.create_confirmation_email(application, self.request)
        try:
            application.confirm()
        except:
            raise Http404

        if msg:
            msg.send()
            try:
                slack.send_slack_invite(request.user.email)
            # Ignore if we can't send, it's only optional
            except SlackInvitationException as e:
                logging.error(e)

        return http.HttpResponseRedirect(reverse('dashboard'))


class CancelApplication(LoginRequiredMixin, UserPassesTestMixin, TabsView):
    template_name = 'cancel.html'

    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get_back_url(self):
        return reverse('dashboard')

    def get_context_data(self, **kwargs):
        context = super(CancelApplication, self).get_context_data(**kwargs)

        application = models.Application.objects.get(user=self.request.user)
        context.update({'application': application, })
        if application.status == models.APP_CANCELLED:
            context.update({'error': "Thank you for responding. We're sorry you won't be able to make it."
                                     " Hope to see you next edition!"
                            })
        elif application.status == models.APP_EXPIRED:
            context.update({'error': "Unfortunately your invite has expired."})
        elif not application.can_be_cancelled():
            context.update({
                'error': "You found a glitch! You can't cancel this invitation. Is this the question for 42?",
                'application': None
            })
        return context

    def post(self, request, *args, **kwargs):
        application = models.Application.objects.get(user=self.request.user)
        try:
            application.cancel()
        except ValidationError:
            pass

        return http.HttpResponseRedirect(reverse('dashboard'))


def get_deadline(application):
    last_updated = application.status_update_date
    if application.status == models.APP_INVITED:
        deadline = last_updated + timedelta(days=7)
    else:
        deadline = last_updated + timedelta(days=1)
    return deadline


class HackerDashboard(LoginRequiredMixin, TabsView):
    template_name = 'dashboard.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerDashboard, self).get_context_data(**kwargs)
        form = forms.ApplicationForm()
        context.update({'form': form})
        try:
            application = models.Application.objects.get(user=self.request.user)
            deadline = get_deadline(application)
            context.update({'invite_timeleft': deadline - timezone.now()})
        except:
            # We ignore this as we are okay if the user has not created an application yet
            pass

        return context

    def post(self, request, *args, **kwargs):
        new_application = True
        try:
            form = forms.ApplicationForm(request.POST, request.FILES, instance=request.user.application)
            new_application = False
        except:
            form = forms.ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            if new_application:
                m = emails.create_application_email(application)
                m.send()
                messages.success(request,
                                 'We have now received your application. '
                                 'Processing your application will take some time, so please be patient.')
            else:
                messages.success(request, 'Application changes saved successfully!')

            return HttpResponseRedirect(reverse('root'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


class HackerApplication(LoginRequiredMixin, TabsView):
    template_name = 'application.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerApplication, self).get_context_data(**kwargs)
        application = get_object_or_404(models.Application, user=self.request.user)
        deadline = get_deadline(application)
        context.update(
            {'invite_timeleft': deadline - timezone.now(), 'form': forms.ApplicationForm(instance=application)})
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = forms.ApplicationForm(request.POST, request.FILES, instance=request.user.application)
        except:
            form = forms.ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()

            messages.success(request, 'Application changes saved successfully!')

            return HttpResponseRedirect(reverse('application'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


class AmbassadorView(LoginRequiredMixin, TabsView):
    template_name = 'ambassador.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AmbassadorView, self).get_context_data(**kwargs)
        try:
            ambassador = models.Ambassador.objects.get(user=self.request.user)
            context.update({'ambassador': ambassador,})
        except(models.Ambassador.DoesNotExist):
            context.update({'form': forms.AmbassadorForm(),})
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = forms.AmbassadorForm(request.POST, request.FILES, instance=request.user.ambassador)
        except:
            form = forms.AmbassadorForm(request.POST, request.FILES)
        if form.is_valid():
            ambassador_apply = form.save(commit=False)
            ambassador_apply.user = request.user
            ambassador_apply.secret_code = new_secret_code()
            ambassador_apply.save()

            messages.success(request, 'Ambassador changes saved successfully!')

            return HttpResponseRedirect(reverse('ambassador'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)
