from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView, RedirectView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.conf import settings

from app.mixins import TabsViewMixin
from app.utils import reverse
from django.shortcuts import redirect
import time
from app.views import TabsView
from applications import models
from checkin.models import CheckIn, SUBJECTS
from applications.models import APP_ATTENDED
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter, RankingListTable
from user.mixins import IsVolunteerMixin, IsOrganizerMixin
from user.models import User


def user_tabs(user):
    return [
        ('Type', reverse('check_in_type'), False),
        ('List', reverse('check_in_list'), False),
        ('QR', reverse('check_in_qr'), False),
    ]


class CheckInType(IsVolunteerMixin, TabsView):
    template_name = 'checkin/choose_type.html'

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CheckInType, self).get_context_data(**kwargs)

        context.update({
            'types': SUBJECTS,
        })

        return context


class CheckInSession(IsVolunteerMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        check_type = kwargs['type']
        for s in SUBJECTS:
            if check_type in s:
                self.request.session['check_type'] = check_type
                self.request.session['type_time'] = str(time.time())

        return reverse('check_in_qr')


class CheckInList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}
    queryset_name = 'applications'

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self, **kwargs):
        ch_type = self.request.session.get('check_type', False)
        if not ch_type:
            return models.Application.objects.filter(pk=0)
        else:
            if (time.time()-float(self.request.session['type_time'])) > settings.TYPE_EXPIRY:
                ch_type = False
                return models.Application.objects.filter(pk=0)

        return models.Application.objects.exclude(
            checkin__in=CheckIn.objects.filter(check_type=ch_type)
        )

    def render_to_response(self, context):
        if not self.request.session.get('check_type', False):
            return redirect('check_in_type')
        else:
            if (time.time()-float(self.request.session['type_time'])) > settings.TYPE_EXPIRY:
                return redirect('check_in_type')

        return super(CheckInList, self).render_to_response(context)


class QRView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/qr.html'

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def render_to_response(self, context):
        if not self.request.session.get('check_type', False):
            return redirect('check_in_type')
        else:
            if (time.time()-float(self.request.session['type_time']))>settings.TYPE_EXPIRY:
                return redirect('check_in_type')

        return super(QRView, self).render_to_response(context)


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)

        appid = kwargs['id']
        app = models.Application.objects.filter(uuid=appid).first()
        ch_type = self.request.session.get('check_type', False)
        for s in SUBJECTS:
            if ch_type in s:
                check_type = s[1]

        if not app or not ch_type:
            raise Http404

        if len(CheckIn.objects.filter(application=app, check_type=ch_type)) > 0:
            checkedin = True
        else:
            checkedin = False

        context.update({
            'app': app,
            'checkedin': checkedin,
            'check_type': check_type,
        })
        try:
            context.update({
                'checkin': CheckIn.objects.filter(application=app).first()
            })
        except:
            pass

        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        app = models.Application.objects.filter(uuid=appid).first()
        ch_type = self.request.session.get('check_type', 'arrived')
        for s in SUBJECTS:
            if ch_type in s:
                check_type = s[1]
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        ci.check_type = ch_type
        ci.save()

        if ch_type == 'arrived':
            ci.application.status = APP_ATTENDED

        messages.success(self.request, '{} successfully \
        checked-in! Good job! Nothing else to see here, \
        you can move on :D'.format(check_type))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
