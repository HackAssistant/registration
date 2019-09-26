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
from django.conf import settings
from app.slack import send_slack_message


def user_tabs(user):
    return [('List', reverse('check_in_list'), False),
            ('Ranking', reverse('check_in_ranking'), False)]


class CheckInList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.objects.exclude(status=models.APP_ATTENDED)


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return 'javascript:history.back()'

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
        qrcode = request.POST.get('qr_code')
        if qrcode is None or qrcode == '':
            messages.success(self.request, 'The QR code is mandatory!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        app = models.Application.objects.filter(uuid=appid).first()
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        ci.qr_identifier = qrcode
        ci.save()
        messages.success(self.request, 'Hacker checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        send_slack_message(app.user.email, 'Hello ' + app.user.name + ' :wave::skin-tone-3:'
                           'and welcome to *HackUPC 2018* :biene:!\nI\'m <@' +
                           settings.SLACK_BOT.get('id', None) + '> and I '
                           ':point_up::skin-tone-3: will be your guide '
                           ':female_mage::skin-tone-3: during the hackathon. '
                           'You can ask :question: me anything you need '
                           ':chocolate_bar:!\n    - Opening ceremony :fast_forward: '
                           'will be at 19h :clock6: on the Vertex building, more '
                           'information on how to get there :world_map: at maps.hackupc.com. '
                           'You can also watch it :tv: live at live.hackupc.com/#/streaming.\n'
                           '    - Hacking :female-technologist::skin-tone-3: starts at 21h, '
                           'but you can look :eyes: for your spot right now.\n'
                           '    - Live schedule :mantelpiece_clock: is available at '
                           'live.hackupc.com.\n    - If you need to leave your baggage '
                           ':handbag:, please go to the infodesk :information_source:.\n'
                           '    - Hardware :pager: will be provided, request it :memo: '
                           'before going to the infodesk :information_source: at '
                           'my.hackupc.com.\n    - If you need technical :three_button_mouse: '
                           'help, ask a mentor :female-teacher::skin-tone-3: at '
                           'mentors.hackupc.com.\nRemember that if I\'m unable to answer '
                           ':speak_no_evil:, you can try with the <#' +
                           settings.SLACK_BOT.get('channel', None) + '> channel '
                           ':speech_balloon: or to any organizer :tshirt: around.\n'
                           '*If there\'s any emergency :rotating_light: seek for any organizer, '
                           'you can also ping <@' + settings.SLACK_BOT.get('director1', None) +
                           '> or <@' + settings.SLACK_BOT.get('director2', None) + '>.*')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckinRankingView(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'checkin/ranking.html'
    table_class = RankingListTable

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return User.objects.annotate(
            checkin_count=Count('checkin__application')).exclude(checkin_count=0)
