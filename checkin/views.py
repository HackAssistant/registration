from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from app.utils import reverse
from app.views import TabsView
from applications import models
from checkin.models import CheckIn
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter, RankingListTable
from user.mixins import IsVolunteerMixin, IsOrganizerMixin
from user.models import User


def user_tabs(user):
    tab = [('Hackers', reverse('check_in_list'), False), ('QR', reverse('check_in_qr'), False)]
    if user.is_organizer():
        tab.extend([('Volunteer', reverse('check_in_volunteer_list'), False),
                    ('Mentor', reverse('check_in_mentor_list'), False),
                    ('Sponsor', reverse('check_in_sponsor_list'), False),
                    ('Ranking', reverse('check_in_ranking'), False)])
    return tab


def get_application_by_type(type, uuid):
    if type == models.userModels.USR_HACKER:
        return models.HackerApplication.objects.filter(uuid=uuid).first()
    elif type == models.userModels.USR_VOLUNTEER:
        return models.VolunteerApplication.objects.filter(uuid=uuid).first()
    elif type == models.userModels.USR_SPONSOR:
        return models.SponsorApplication.objects.filter(uuid=uuid).first()
    elif type == models.userModels.USR_MENTOR:
        return models.MentorApplication.objects.filter(uuid=uuid).first()
    return None


class CheckInList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=models.APP_CONFIRMED)


class QRView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/qr.html'

    def get_current_tabs(self):
        return user_tabs(self.request.user)


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        type = kwargs['type']
        type = models.userModels.USR_URL_TYPE[type]
        app = get_application_by_type(type, appid)
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
        type = request.POST.get('type')
        app = get_application_by_type(type, appid)
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.set_application(app)
        ci.save()
        messages.success(self.request, 'User checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckinRankingView(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'checkin/ranking.html'
    table_class = RankingListTable

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return User.objects.annotate(
            checkin_count=Count('checkin__application')).exclude(checkin_count=0)


class CheckinOtherUserList(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return user_tabs(self.request.user)


class CheckinVolunteerList(CheckinOtherUserList):
    def get_queryset(self):
        return models.VolunteerApplication.objects.filter(status=models.APP_CONFIRMED)


class CheckinMentorList(CheckinOtherUserList):
    def get_queryset(self):
        return models.MentorApplication.objects.filter(status=models.APP_CONFIRMED)


class CheckinSponsorList(CheckinOtherUserList):
    def get_queryset(self):
        return models.SponsorApplication.objects.filter(status=models.APP_CONFIRMED)
