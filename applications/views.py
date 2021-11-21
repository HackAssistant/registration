# Create your views here.
from __future__ import print_function

import logging
from datetime import timedelta

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView

from app import slack
from app.slack import SlackInvitationException
from app.utils import reverse, hacker_tabs
from app.views import TabsView
from applications import models, emails, forms
from organizers.tables import SponsorFilter, SponsorListTableWithNoAction
from organizers.views import _OtherApplicationsListView
from user.mixins import IsHackerMixin, is_hacker, IsSponsorMixin, DashboardMixin
from user import models as userModels

VIEW_APPLICATION_TYPE = {
    userModels.USR_HACKER: models.HackerApplication,
    userModels.USR_VOLUNTEER: models.VolunteerApplication,
    userModels.USR_MENTOR: models.MentorApplication,
}

VIEW_APPLICATION_FORM_TYPE = {
    userModels.USR_HACKER: forms.HackerApplicationForm,
    userModels.USR_VOLUNTEER: forms.VolunteerApplicationForm,
    userModels.USR_MENTOR: forms.MentorApplicationForm,
}


def check_application_exists(user, uuid):
    try:
        application = VIEW_APPLICATION_TYPE.get(user.type, models.HackerApplication).objects.get(user=user)
    except (models.HackerApplication.DoesNotExist or models.VolunteerApplication.DoesNotExist or
            models.SponsorApplication.DoesNotExist or models.MentorApplication.DoesNotExist):
        raise Http404
    if not application or uuid != application.uuid_str:
        raise Http404


class ConfirmApplication(IsHackerMixin, UserPassesTestMixin, View):
    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get(self, request, *args, **kwargs):
        Application = VIEW_APPLICATION_TYPE.get(self.request.user.type, models.HackerApplication)
        application = Application.objects.get(user=request.user)
        msg = None
        if application.can_confirm():
            msg = emails.create_confirmation_email(application, self.request)
        try:
            application.confirm()
        except Exception:
            raise Http404

        if msg:
            msg.send()
            try:
                slack.send_slack_invite(request.user.email)
            # Ignore if we can't send, it's only optional
            except SlackInvitationException as e:
                logging.error(e)

        return http.HttpResponseRedirect(reverse('dashboard'))


class CancelApplication(IsHackerMixin, UserPassesTestMixin, TabsView):
    template_name = 'cancel.html'

    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get_back_url(self):
        return reverse('dashboard')

    def get_context_data(self, **kwargs):
        context = super(CancelApplication, self).get_context_data(**kwargs)

        Application = VIEW_APPLICATION_TYPE.get(self.request.user.type, models.HackerApplication)

        application = Application.objects.get(user=self.request.user)
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
        Application = VIEW_APPLICATION_TYPE.get(self.request.user.type, models.HackerApplication)

        application = Application.objects.get(user=self.request.user)
        try:
            application.cancel()
        except ValidationError:
            pass

        return http.HttpResponseRedirect(reverse('dashboard'))


def get_deadline(application):
    last_updated = application.status_update_date
    if application.status == models.APP_INVITED:
        deadline = last_updated + timedelta(days=5)
    else:
        deadline = last_updated + timedelta(days=1)
    return deadline


class HackerDashboard(DashboardMixin, TabsView):
    template_name = 'dashboard.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerDashboard, self).get_context_data(**kwargs)
        Application = VIEW_APPLICATION_TYPE.get(self.request.user.type, models.HackerApplication)
        ApplicationForm = VIEW_APPLICATION_FORM_TYPE.get(self.request.user.type, forms.HackerApplicationForm)
        try:
            draft = models.DraftApplication.objects.get(user=self.request.user)
            dict = draft.get_dict()
            app = Application({'dict': dict})
            form = ApplicationForm(instance=app)
        except Exception:
            form = ApplicationForm()
        context.update({'form': form, 'is_hacker': self.request.user.is_hacker()})
        try:
            application = Application.objects.get(user=self.request.user)
            deadline = get_deadline(application)
            context.update({'invite_timeleft': deadline - timezone.now(), 'application': application})
        except Exception:
            # We ignore this as we are okay if the user has not created an application yet
            pass

        return context

    def post(self, request, *args, **kwargs):
        ApplicationForm = VIEW_APPLICATION_FORM_TYPE.get(self.request.user.type, forms.HackerApplicationForm)

        new_application = True
        try:
            form = ApplicationForm(request.POST, request.FILES, instance=request.user.application)
            new_application = False
        except Exception:
            form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            email_subscribe = form.cleaned_data.get('email_subscribe', False)
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            if email_subscribe:
                application.user.email_subscribed = email_subscribe
                application.user.save()
            if new_application:
                messages.success(request,
                                 'We have now received your application. '
                                 'Processing your application will take some time, so please be patient.')
            else:
                messages.success(request, 'Application changes saved successfully!')
            if user_is_in_blacklist(application.user):
                application.set_blacklist()

            return HttpResponseRedirect(reverse('root'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


class HackerApplication(IsHackerMixin, TabsView):
    template_name = 'application.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerApplication, self).get_context_data(**kwargs)

        Application = VIEW_APPLICATION_TYPE.get(self.request.user.type, models.HackerApplication)
        ApplicationForm = VIEW_APPLICATION_FORM_TYPE.get(self.request.user.type, forms.HackerApplicationForm)

        application = get_object_or_404(Application, user=self.request.user)
        deadline = get_deadline(application)
        form = ApplicationForm(instance=application)
        if not application.can_be_edit():
            form.set_read_only()
        context.update(
            {'invite_timeleft': deadline - timezone.now(), 'form': form, 'is_hacker': self.request.user.is_hacker()})
        return context

    def post(self, request, *args, **kwargs):
        ApplicationForm = VIEW_APPLICATION_FORM_TYPE.get(self.request.user.type, forms.HackerApplicationForm)
        try:
            form = ApplicationForm(request.POST, request.FILES,
                                   instance=request.user.application)
        except Exception:
            form = ApplicationForm(request.POST, request.FILES)
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


class SponsorApplicationView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SponsorApplicationView, self).get_context_data(**kwargs)
        form = forms.SponsorForm()
        context.update({'form': form, 'is_sponsor': True})
        try:
            uid = force_text(urlsafe_base64_decode(self.kwargs.get('uid', None)))
            user = userModels.User.objects.get(pk=uid)
            context.update({'user': user})
        except (TypeError, ValueError, OverflowError, userModels.User.DoesNotExist):
            pass

        return context

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(self.kwargs.get('uid', None)))
            user = userModels.User.objects.get(pk=uid)
            real_token = userModels.Token.objects.get(pk=user).uuid_str()
            token = self.kwargs.get('token', None)
        except (TypeError, ValueError, OverflowError, userModels.User.DoesNotExist, userModels.Token.DoesNotExist):
            raise Http404('Invalid url')
        if token != real_token:
            raise Http404('Invalid url')
        if not user.has_applications_left():
            raise Http404('You have no applications left')
        return super(SponsorApplicationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.SponsorForm(request.POST, request.FILES)
        try:
            uid = force_text(urlsafe_base64_decode(self.kwargs.get('uid', None)))
            user = userModels.User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, userModels.User.DoesNotExist):
            return Http404('How did you get here?')
        if not user.has_applications_left():
            form.add_error(None, 'You have no applications left')
        elif form.is_valid():
            name = form.cleaned_data['name']
            app = models.SponsorApplication.objects.filter(user=user, name=name).first()
            if app:
                form.add_error('name', 'This name is already taken. Have you applied?')
            else:
                application = form.save(commit=False)
                application.user = user
                application.save()
                messages.success(request, 'We have now received your application. ')
                return render(request, 'sponsor_submitted.html')
        c = self.get_context_data()
        c.update({'form': form})
        return render(request, self.template_name, c)


class ConvertHackerToMentor(TemplateView):
    template_name = 'convert_mentor.html'

    def get(self, request, *args, **kwargs):
        if request.user.application.is_invalid():
            return super(ConvertHackerToMentor, self).get(request, *args, **kwargs)
        return Http404

    def post(self, request, *args, **kwargs):
        if request.user.application.is_invalid():
            request.user.set_mentor()
            request.user.save()
            messages.success(request, 'Thanks for coming as mentor!')
        else:
            messages.error(request, 'You have no permissions to do this')
        return HttpResponseRedirect(reverse('dashboard'))


class SponsorDashboard(IsSponsorMixin, _OtherApplicationsListView):
    table_class = SponsorListTableWithNoAction
    filterset_class = SponsorFilter

    def get_current_tabs(self):
        return None

    def get_queryset(self):
        return models.SponsorApplication.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SponsorDashboard, self).get_context_data(**kwargs)
        context['otherApplication'] = True
        context['emailCopy'] = False
        return context


@is_hacker
def save_draft(request):
    Application = VIEW_APPLICATION_TYPE.get(request.user.type, models.HackerApplication)
    ApplicationForm = VIEW_APPLICATION_FORM_TYPE.get(request.user.type, forms.HackerApplicationForm)
    d = models.DraftApplication()
    d.user = request.user
    form_keys = set(dict(ApplicationForm().fields).keys())
    valid_keys = set([field.name for field in Application()._meta.get_fields()])
    d.save_dict(dict((k, v) for k, v in request.POST.items() if k in valid_keys.intersection(form_keys) and v))
    d.save()
    return JsonResponse({'saved': True})


def user_is_in_blacklist(user):
    result = True
    blacklist_user = models.BlacklistUser.objects.filter(email=user.email).first()
    if not blacklist_user:
        blacklist_user = models.BlacklistUser.objects.filter(name=user.name).first()
        if not blacklist_user:
            result = False
    return result
