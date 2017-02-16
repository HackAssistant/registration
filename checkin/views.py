from checkin.tables import ApplicationsTable
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from register import models


class CheckInList(PermissionRequiredMixin, TemplateView):
    permission_required = 'application.attended_application'
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


class CheckInHackerView(PermissionRequiredMixin, TemplateView):
    template_name = 'checkin/hacker.html'
    permission_required = 'application.attended_application'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        context.update({
            'app': (models.Application.objects.get(id=appid)),
        })
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        app = models.Application.objects.get(id=appid)
        app.check_in()
        return HttpResponseRedirect(reverse('check_in_list'))
