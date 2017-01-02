# Create your views here.
from __future__ import print_function

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from register import models
from register.forms import ApplicationsTypeform


class UpdateApplications(View):
    def get(self, request):
        return HttpResponse(ApplicationsTypeform().update_forms())


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
        if request.POST.get('decline'):
            vote_type = models.VOTE_NEGATIVE

        add_vote(self.get_next_application(), request.user, vote_type)
        return HttpResponseRedirect(reverse('vote'))

    def get_context_data(self, **kwargs):
        context = super(VoteApplicationView, self).get_context_data(**kwargs)
        application = self.get_next_application()

        context['app'] = application
        context["dp_image_src"] = "https://maxcdn.icons8.com/Share/icon/ios7/Logos//devpost1600.png"
        context["github_image_src"] = "https://cdn4.iconfinder.com/data/icons/iconsimple-logotypes/512/github-512.png"
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


class CancelApplication(View):
    def get(self, request, token):
        application = models.Application.objects.get(id=token)
        application.cancel()
        return HttpResponse('CANCELLED')
