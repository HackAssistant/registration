from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from applications import models
from checkin.models import CheckIn
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter
from user.mixins import IsVolunteerMixin
from user.models import User


class CheckInList(IsVolunteerMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 100}

    def get_queryset(self):
        return models.Application.objects.filter(status=models.APP_CONFIRMED)


class CheckInAllList(CheckInList):
    template_name = 'checkin/list_all.html'

    def get_queryset(self):
        return models.Application.objects.exclude(status=models.APP_ATTENDED)


class QRView(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/qr.html'


class CheckInHackerView(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/hacker.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        app = models.Application.objects.filter(uuid=appid).first()
        if not app:
            raise Http404
        context.update({
            'app': app,
            'checkedin': app.status == models.APP_ATTENDED
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        app = models.Application.objects.filter(uuid=appid).first()
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        ci.save()
        messages.success(self.request, 'Hacker checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckinRankingView(IsVolunteerMixin, TemplateView):
    template_name = 'checkin/ranking.html'

    def get_context_data(self, **kwargs):
        context = super(CheckinRankingView, self).get_context_data(**kwargs)
        context['ranking'] = User.objects.annotate(
            checkin_count=Count('checkin__application')) \
            .order_by('-checkin_count').exclude(checkin_count=0).values('checkin_count',
                                                                        'email')
        return context
