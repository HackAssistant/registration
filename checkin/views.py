from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from app.views import TabsView
from applications import models
from checkin.models import CheckIn
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter, \
    SponsorApplicationsCheckInTable, SponsorApplicationCheckinFilter
from user.mixins import IsVolunteerMixin, HaveVolunteerPermissionMixin, HaveMentorPermissionMixin, \
    HaveSponsorPermissionMixin
from organizers.views import volunteer_tabs, mentor_tabs, hacker_tabs, sponsor_tabs


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
        if self.request.user.is_volunteer_accepted:
            return None
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=models.APP_CONFIRMED)


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        type = kwargs['type']
        type = models.userModels.USR_URL_TYPE_CHECKIN[type]
        app = get_application_by_type(type, appid)
        if not app:
            raise Http404
        context.update({
            'app': app,
            'checkedin': app.status == models.APP_ATTENDED
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except Exception:
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


class CheckinOtherUserList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}


class CheckinVolunteerList(HaveVolunteerPermissionMixin, CheckinOtherUserList):
    def get_queryset(self):
        return models.VolunteerApplication.objects.filter(status=models.APP_CONFIRMED)

    def get_current_tabs(self):
        return volunteer_tabs(self.request.user)


class CheckinMentorList(HaveMentorPermissionMixin, CheckinOtherUserList):
    def get_queryset(self):
        return models.MentorApplication.objects.filter(status=models.APP_CONFIRMED)

    def get_current_tabs(self):
        return mentor_tabs(self.request.user)


class CheckinSponsorList(HaveSponsorPermissionMixin, CheckinOtherUserList):
    table_class = SponsorApplicationsCheckInTable
    filterset_class = SponsorApplicationCheckinFilter

    def get_queryset(self):
        return models.SponsorApplication.objects.filter(status=models.APP_CONFIRMED)

    def get_current_tabs(self):
        return sponsor_tabs(self.request.user)
