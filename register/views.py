# Create your views here.
from __future__ import print_function

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from register import models
from register.forms import ApplicationsTypeform


class UpdateApplications(View):
    def get(self, request):
        return http.HttpResponse(ApplicationsTypeform().update_forms())


def root_view(request):
    return HttpResponseRedirect(reverse('vote'))


def add_vote(application, user, vote_type):
    v = models.Vote()
    v.user = user
    v.application = application
    v.vote = vote_type
    v.save()
    return v


class VoteApplicationView(LoginRequiredMixin, TemplateView):
    template_name = 'vote.html'

    def get_next_application(self):
        """
        Django model to the rescue. This is transformed to an SQL sentence that does exactly what we need
        :return: pending aplication that has not been voted by the current user and that has less votes and its older
        """
        return models.Application.objects \
            .exclude(vote__user_id=self.request.user.id) \
            .filter(status='P') \
            .annotate(count=Count('vote')) \
            .order_by('count', 'submission_date') \
            .first()

    def post(self, request, *args, **kwargs):

        vote_type = models.VOTE_SKIP
        if request.POST.get('accept'):
            vote_type = models.VOTE_POSITIVE
        elif request.POST.get('decline'):
            vote_type = models.VOTE_NEGATIVE
        application = models.Application.objects.get(id=request.POST.get('app_id'))
        add_vote(application, request.user, vote_type)
        return HttpResponseRedirect(reverse('vote'))

    def get_context_data(self, **kwargs):
        context = super(VoteApplicationView, self).get_context_data(**kwargs)
        context['app'] = self.get_next_application()
        return context


class ConfirmApplication(TemplateView):
    template_name = 'confirm.html'

    def get_context_data(self, **kwargs):
        context = super(ConfirmApplication, self).get_context_data(**kwargs)
        application = models.Application.objects.get(id=context['token'])
        request = self.request
        already_confirmed = application.is_confirmed()
        cancellation_url = application.cancelation_url(request)
        try:
            application.confirm(cancellation_url)
            context.update({
                'application': application,
                'cancel': cancellation_url,
                'reconfirming': already_confirmed
            })
        except ValidationError as e:
            context.update({
                'application': application,
                'error': "This application hasn't been invited yet.",
            })

        return context


class CancelApplication(TemplateView):
    template_name = 'cancel.html'

    def get_context_data(self, **kwargs):
        context = super(CancelApplication, self).get_context_data(**kwargs)
        try:
            application = models.Application.objects.get(id=context['token'])
        except models.Application.DoesNotExist:
            raise http.Http404

        context.update({
            'application': application,
        })

        if application.status == models.APP_CANCELLED:
            context.update({
                'error':
                    """
                    Thank you for responding.
                     We're sorry you won't be able to make it to HackUPC. Hope to see you next edition!
                    """
            })
        elif not application.can_be_cancelled():
            context.update({
                'error':
                    """
                    You found a glitch! You are trying to cancel a non invited application.
                    Is this the question to 42?
                    """,
                'application': None
            })

        return context

    def post(self, request, *args, **kwargs):
        application = models.Application.objects.get(id=kwargs['token'])
        try:
            application.cancel()
        except ValidationError:
            pass

        return http.HttpResponseRedirect(reverse('cancel_app', args=(application.id,)))
