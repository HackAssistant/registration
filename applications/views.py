# Create your views here.
from __future__ import print_function

import logging
from datetime import timedelta

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from app import slack
from app.slack import SlackInvitationException
from app.utils import reverse
from applications import models, emails, forms


def check_application_exists(user, uuid):
    try:
        application = models.Application.objects.get(user=user)
    except models.Application.DoesNotExist:
        raise Http404
    if not application or uuid != application.uuid_str:
        raise Http404


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


class CancelApplication(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'cancel.html'

    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

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


def create_phase(phase_key, title, finished_func, user):
    is_finished = False
    try:
        is_finished = bool(finished_func(user))
    except:
        pass

    return {'template': 'phases/' + phase_key + '.html',
            'finished': is_finished, 'title': title, 'key': phase_key}


def get_deadline(application):
    last_updated = application.status_update_date
    if application.status == models.APP_INVITED:
        deadline = last_updated + timedelta(days=5)
    else:
        deadline = last_updated + timedelta(days=1)
    return deadline


def get_current_phase(phases):
    try:
        current = [p for p in phases if not p['finished']][0]
    except IndexError:
        current = [p for p in phases if p['finished']][-1]
    return current


class HackerDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(HackerDashboard, self).get_context_data(**kwargs)

        phases = self.get_phases()
        current = get_current_phase(phases)
        active = self.get_active_phase(current, phases)
        form = forms.ApplicationForm()
        context.update({'phases': phases, 'current': current,
                        'active': active, 'form': form})
        try:
            application = self.get_current_app(self.request.user)
            form = forms.ApplicationForm(instance=application)
            context.update({'form': form})
            deadline = get_deadline(application)
            context.update({'invite_timeleft': deadline - timezone.now()})
        except:
            # We ignore this as we are okay if the user has not created an application yet
            pass

        return context

    def get_active_phase(self, current, phases):
        active_key = self.request.GET.get('phase', None)
        active = current
        if active_key:
            try:
                active = [p for p in phases if p['key'] == active_key][0]
            except:
                pass
        return active

    def get_phases(self):
        user = self.request.user
        phases = [
            create_phase('verify', "Email verification",
                         lambda x: x.email_verified, user),
            create_phase('general', "General information",
                         lambda x: x.application, user),
            create_phase('application', "Application status", lambda x: x.application.answered_invite(),
                         self.request.user)
        ]

        # Try/Except caused by Hacker not existing
        try:
            current_app = self.get_current_app(user)
            if current_app.status == models.APP_ATTENDED:
                phases.append(
                    create_phase('live', "Live", lambda x: True,
                                 self.request.user)
                )
        except:
            pass

        return phases

    def get_current_app(self, user):
        return models.Application.objects.get(user=user)

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
                messages.success(request,
                                 'We have now received your application. '
                                 'Processing your application will take some time, so please be patient.')
            else:
                messages.info(request, 'Application changes saved successfully!')

            return HttpResponseRedirect(reverse('root'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


def code_conduct(request):
    return render(request, 'code_conduct.html')
