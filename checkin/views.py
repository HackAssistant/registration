from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from checkin.models import CheckIn
from checkin.tables import ApplicationsTable
from hackers import models
from user.mixins import IsVolunteerMixin


class CheckInList(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/list.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInList, self).get_context_data(**kwargs)
        attended = self.get_applications()
        table = ApplicationsTable(attended)
        context.update({
            'applicationsTable': table,
        })
        return context

    def get_applications(self):
        return models.Application.objects.filter(status=models.APP_CONFIRMED)


class CheckInAllList(CheckInList):
    template_name = 'checkin/list_all.html'

    def get_applications(self):
        return models.Application.objects.exclude(status=models.APP_ATTENDED)


class QRView(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/qr.html'


class CheckInHackerView(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/hacker.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        app = get_object_or_404(models.Application, pk=appid)
        context.update({
            'app': app,
            'hacker': app.hacker,
            'checkedin': app.status == models.APP_ATTENDED
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        lopd_signed = request.POST.get('checkin') == 'checkin_lopd'
        app = models.Application.objects.get(id=appid)
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        ci.signed_lopd = lopd_signed
        ci.save()
        messages.success(self.request, 'Hacker checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
