import json

from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse

from app.mixins import TabsViewMixin
from app.utils import reverse
from app.views import TabsView
from applications import models as appmodels
from user import models
from checkin.models import CheckIn
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter, \
    SponsorApplicationsCheckInTable, SponsorApplicationCheckinFilter
from user.mixins import IsVolunteerMixin, HaveVolunteerPermissionMixin, HaveMentorPermissionMixin, \
    HaveSponsorPermissionMixin
from app.slack import send_slack_message
from multiprocessing import Pool
from organizers.views import volunteer_tabs, mentor_tabs, hacker_tabs, sponsor_tabs


def get_application_by_type(type, uuid):
    if type == models.USR_HACKER:
        return appmodels.HackerApplication.objects.filter(uuid=uuid).first()
    elif type == models.USR_VOLUNTEER:
        return appmodels.VolunteerApplication.objects.filter(uuid=uuid).first()
    elif type == models.USR_SPONSOR:
        return appmodels.SponsorApplication.objects.filter(uuid=uuid).first()
    elif type == models.USR_MENTOR:
        return appmodels.MentorApplication.objects.filter(uuid=uuid).first()
    return None


def checking_in_hacker(request, web, appid, qrcode, type):
    if qrcode is None or qrcode == '':
        return False
    app = get_application_by_type(type, appid)
    if not app:
        return False
    ci = CheckIn()
    if web:
        ci.user = request.user
    else:
        ci.user = appmodels.HackerApplication.objects.filter(user=1).first().user
    ci.set_application(app)
    ci.qr_identifier = qrcode
    ci.save()
    try:
        pool = Pool(processes=1)
        pool.apply_async(send_slack_message, [app.user.email, 'Hello ' + app.user.name + ' :wave::skin-tone-3:'
                                              'and welcome to *HackUPC 2019* :bee:!\n    - Opening ceremony '
                                              ':fast_forward: will be at 19h :clock6: on the Vèrtex building, more '
                                              'information on how to get there :world_map: at maps.hackupc.com. '
                                              'You can also watch it :tv: live at live.hackupc.com/#/streaming.\n'
                                              '    - Hacking :female-technologist::skin-tone-3: starts at 21h, '
                                              'but you can look :eyes: for your spot right now, *building A5 is '
                                              'currently closed :door: and will be available after the opening '
                                              'ceremony*.\n    - Live schedule :mantelpiece_clock: is available at '
                                              'live.hackupc.com.\n    - If you need to leave your baggage '
                                              ':handbag:, please go to the infodesk :information_source:.\n'
                                              '    - Hardware :pager: will be provided, request it :memo: '
                                              'before going to the infodesk :information_source: at '
                                              'my.hackupc.com.\n    - If you need technical :three_button_mouse: '
                                              'help, ask a mentor :female-teacher::skin-tone-3: at '
                                              'mentors.hackupc.com.\nRemember that if you have a question, '
                                              'try the <#' + settings.SLACK_BOT.get('channel', None) + '> channel '
                                              ':speech_balloon: or just ask any organizer :tshirt: around.\n'
                                              '*If there\'s an emergency :rotating_light: seek for an organizer, '
                                              'you can also ping <@' + settings.SLACK_BOT.get('director1', None) +
                                              '> or <@' + settings.SLACK_BOT.get('director2', None) + '>.*'])
    except TypeError:
        pass
    return True


class CheckInList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return appmodels.HackerApplication.objects.filter(status=appmodels.APP_CONFIRMED)


class CheckInJudgeList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        checkins = CheckIn.objects.values_list("application__user__id", flat=True)
        return models.User.objects.filter(is_judge=True).exclude(id__in=checkins)


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        type = kwargs['type']
        type = models.USR_URL_TYPE_CHECKIN[type]
        app = get_application_by_type(type, appid)
        if not app:
            raise Http404
        if app:
            context.update({
                'app': app,
                'checkedin': app.status == appmodels.APP_ATTENDED
            })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        type = request.POST.get('type')
        qrcode = request.POST.get('qr_code')
        if checking_in_hacker(request, True, appid, qrcode, type):
            messages.success(self.request, 'Hacker checked-in! Good job! '
                                           'Nothing else to see here, '
                                           'you can move on :D')
        else:
            messages.success(self.request, 'The QR code is mandatory!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckinOtherUserList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}


class CheckinVolunteerList(HaveVolunteerPermissionMixin, CheckinOtherUserList):
    def get_queryset(self):
        return appmodels.VolunteerApplication.objects.filter(status=appmodels.APP_CONFIRMED)

    def get_current_tabs(self):
        return volunteer_tabs(self.request.user)


class CheckinMentorList(HaveMentorPermissionMixin, CheckinOtherUserList):
    def get_queryset(self):
        return appmodels.MentorApplication.objects.filter(status=appmodels.APP_CONFIRMED)

    def get_current_tabs(self):
        return mentor_tabs(self.request.user)


class CheckinSponsorList(HaveSponsorPermissionMixin, CheckinOtherUserList):
    table_class = SponsorApplicationsCheckInTable
    filterset_class = SponsorApplicationCheckinFilter

    def get_queryset(self):
        return appmodels.SponsorApplication.objects.filter(status=appmodels.APP_CONFIRMED)

    def get_current_tabs(self):
        return sponsor_tabs(self.request.user)


class CheckInAPI(APIView):

    def get(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != settings.MEALS_TOKEN:
            return HttpResponse(status=403)
        checkins = CheckIn.objects.values_list("application__user__id", flat=True)
        ids = [u.id for u in models.User.objects.exclude(id__in=checkins) if not u.is_participant]
        checkInData = models.User.objects.filter(id__in=ids)
        checkInDataList = []
        for e in checkInData:
            app = appmodels.HackerApplication.objects.filter(user__id=e.id).first()
            if app:
                checkInDataList.append({'uuid': str(e.id), 'id': e.id, 'name': e.name, 'email': e.email,
                                        "tSize": app.tshirt_size, "diet": app.diet})
            else:
                checkInDataList.append({'uuid': str(e.id), 'id': e.id, 'name': e.name, 'email': e.email,
                                        "tSize": "Unknown", "diet": "Unknown"})
        return HttpResponse(json.dumps({'code': 1, 'content': checkInDataList}), content_type='application/json')

    def post(self, request, format=None):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        content = body['content']
        var_token = content['token']
        if var_token != settings.MEALS_TOKEN:
            return HttpResponse(status=500)
        userid = content['app_id']
        qrcode = content['qr_code']
        if checking_in_hacker(request, False, userid, qrcode):
            return JsonResponse({'code': 1, 'message': 'Hacker Checked in'})
        return JsonResponse({'code': 0, 'message': 'Invalid QR'})
