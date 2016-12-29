# Create your views here.
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from register import models
from register.forms import ApplicationsTypeform


class UpdateApplications(View):
    def get(self, request):
        return HttpResponse(ApplicationsTypeform().update_forms())


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
