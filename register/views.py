# Create your views here.
from django import http
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from register import models
from register.forms import ApplicationsTypeform


class UpdateApplications(View):
    def get(self, request):
        return http.HttpResponse(ApplicationsTypeform().update_forms())


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
                     We're sorry you won't be able to make it to. Hope to see you next edition!
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

        return render(request, self.template_name, self.get_context_data(**kwargs))
