# Create your views here.
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Avg, F
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from app import slack
from app.mixins import TabsViewMixin
from app.slack import SlackInvitationException
from applications import emails
from applications.emails import send_batch_emails
from applications.models import APP_PENDING, APP_DUBIOUS, APP_INVALID
from organizers import models
from organizers.models import Vote
from organizers.tables import ApplicationsListTable, ApplicationFilter, AdminApplicationsListTable, RankingListTable, \
    AdminTeamListTable, InviteFilter, DubiousListTable, DubiousApplicationFilter, VolunteerFilter, VolunteerListTable, \
    MentorListTable, MentorFilter, SponsorListTable, SponsorFilter
from teams.models import Team
from user.mixins import IsOrganizerMixin, IsDirectorMixin


def add_vote(application, user, tech_rat, pers_rat):
    v = models.Vote()
    v.user = user
    v.application = application
    v.tech = tech_rat
    v.personal = pers_rat
    v.save()
    return v


def add_comment(application, user, text):
    comment = models.ApplicationComment()
    comment.author = user
    comment.application = application
    comment.text = text
    comment.save()
    return comment


def organizer_tabs(user):
    t = [('Applications', reverse('app_list'), False),
         ('Review', reverse('review'),
          'new' if models.HackerApplication.objects.exclude(vote__user_id=user.id).filter(status=APP_PENDING) else ''),
         ('Ranking', reverse('ranking'), False),
         ('Volunteers', reverse('volunteer_list'), False),
         ('Mentors', reverse('mentor_list'), False),
         ('Sponsor', reverse('sponsor_list'), False),
         ]
    if user.has_dubious_access and getattr(settings, 'DUBIOUS_ENABLED', False):
        t.append(('Dubious', reverse('dubious'),
                  'new' if models.HackerApplication.objects.filter(status=APP_DUBIOUS,
                                                                   contacted=False).count() else ''))
    return t


class RankingView(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'ranking.html'
    table_class = RankingListTable
    table_pagination = False

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Vote.objects.exclude(application__status__in=[APP_DUBIOUS, APP_INVALID]) \
            .annotate(email=F('user__email')) \
            .values('email').annotate(total_count=Count('application'),
                                      skip_count=Count('application') - Count('calculated_vote'),
                                      vote_count=Count('calculated_vote')) \
            .exclude(vote_count=0)


class ApplicationsListView(TabsViewMixin, IsOrganizerMixin, ExportMixin, SingleTableMixin, FilterView):
    template_name = 'applications_list.html'
    table_class = ApplicationsListTable
    filterset_class = ApplicationFilter
    table_pagination = {'per_page': 100}
    exclude_columns = ('detail', 'status', 'vote_avg')
    export_name = 'applications'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.annotate_vote(models.HackerApplication.objects.all())

    def get_context_data(self, **kwargs):
        context = super(ApplicationsListView, self).get_context_data(**kwargs)
        context['otherApplication'] = False
        return context


class InviteListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, FilterView):
    template_name = 'invite_list.html'
    table_class = AdminApplicationsListTable
    filterset_class = InviteFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.annotate_vote(models.HackerApplication.objects.filter(status=APP_PENDING))

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.HackerApplication.objects.filter(pk__in=ids).all()
        mails = []
        errors = 0
        for app in apps:
            try:
                app.invite(request.user)
                m = emails.create_invite_email(app, request)
                mails.append(m)
            except ValidationError:
                errors += 1
        if mails:
            send_batch_emails(mails)
            messages.success(request, "%s applications invited" % len(mails))
        else:
            errorMsg = "No applications invited"
            if errors != 0:
                errorMsg = "%s applications not invited" % errors
            messages.error(request, errorMsg)

        return HttpResponseRedirect(reverse('invite_list'))


class ApplicationDetailView(TabsViewMixin, IsOrganizerMixin, TemplateView):
    template_name = 'application_detail.html'

    def get_back_url(self):
        return reverse('app_list')

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetailView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context['app'] = application
        context['vote'] = self.can_vote()
        context['comments'] = models.ApplicationComment.objects.filter(application=application)
        if application and getattr(application.user, 'team', False) and settings.TEAMS_ENABLED:
            context['teammates'] = Team.objects.filter(team_code=application.user.team.team_code) \
                .values('user__name', 'user__email', 'user')

            for mate in context['teammates']:
                if application.user.id == mate['user']:
                    mate['is_me'] = True
                    continue

                mate_app = models.HackerApplication.objects.filter(user=mate['user']).first()
                if mate_app:
                    mate['app_uuid_str'] = mate_app.uuid_str

        return context

    def can_vote(self):
        return False

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.HackerApplication.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('app_id')
        application = models.HackerApplication.objects.get(pk=id_)

        comment_text = request.POST.get('comment_text', None)
        if request.POST.get('add_comment'):
            add_comment(application, request.user, comment_text)
        elif request.POST.get('invite') and request.user.is_director:
            self.invite_application(application)
        elif request.POST.get('confirm') and request.user.is_director:
            self.confirm_application(application)
        elif request.POST.get('cancel') and request.user.is_director:
            self.cancel_application(application)
        elif request.POST.get('waitlist') and request.user.is_director:
            self.waitlist_application(application)
        elif request.POST.get('slack') and request.user.check_is_organizer:
            self.slack_invite(application)
        elif request.POST.get('set_dubious') and request.user.check_is_organizer:
            application.set_dubious()
        elif request.POST.get('contact_user') and request.user.has_dubious_access:
            application.set_contacted(request.user)
        elif request.POST.get('unset_dubious') and request.user.has_dubious_access:
            add_comment(application, request.user,
                        "Dubious review result: No problems, hacker allowed to participate in hackathon!")
            application.unset_dubious()
        elif request.POST.get('invalidate') and request.user.has_dubious_access:
            add_comment(application, request.user,
                        "Dubious review result: Hacker is not allowed to participate in hackathon.")
            application.invalidate()

        return HttpResponseRedirect(reverse('app_detail', kwargs={'id': application.uuid_str}))

    def waitlist_application(self, application):
        try:
            application.reject(self.request)
            messages.success(self.request, "%s application wait listed" % application.user.email)
        except ValidationError as e:
            messages.error(self.request, e.message)

    def slack_invite(self, application):
        try:
            slack.send_slack_invite(application.user.email)
            messages.success(self.request, "Slack invite sent to %s" % application.user.email)
        except SlackInvitationException as e:
            messages.error(self.request, "Slack error: %s" % str(e))

    def cancel_application(self, application):
        try:
            application.cancel()
            messages.success(self.request, "%s application cancelled" % application.user.email)
        except ValidationError as e:
            messages.error(self.request, e.message)

    def confirm_application(self, application):
        try:
            application.confirm()
            messages.success(self.request, "Ticket to %s successfully sent" % application.user.email)
            m = emails.create_confirmation_email(application, self.request)
            m.send()
        except ValidationError as e:
            messages.error(self.request, e.message)

    def invite_application(self, application):
        try:
            application.invite(self.request.user)
            messages.success(self.request, "Invite to %s successfully sent" % application.user.email)
            m = emails.create_invite_email(application, self.request)
            m.send()
        except ValidationError as e:
            messages.error(self.request, e.message)


class ReviewApplicationView(ApplicationDetailView):
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_back_url(self):
        return None

    def get_application(self, kwargs):
        """
        Django model to the rescue. This is transformed to an SQL sentence
        that does exactly what we need
        :return: pending aplication that has not been voted by the current
        user and that has less votes and its older
        """
        max_votes_to_app = getattr(settings, 'MAX_VOTES_TO_APP', 50)
        return models.HackerApplication.objects \
            .exclude(vote__user_id=self.request.user.id, user_id=self.request.user.id) \
            .filter(status=APP_PENDING) \
            .annotate(count=Count('vote__calculated_vote')) \
            .filter(count__lte=max_votes_to_app) \
            .order_by('count', 'submission_date') \
            .first()

    def get(self, request, *args, **kwargs):
        r = super(ReviewApplicationView, self).get(request, *args, **kwargs)
        return r

    def post(self, request, *args, **kwargs):
        tech_vote = request.POST.get('tech_rat', None)
        pers_vote = request.POST.get('pers_rat', None)
        comment_text = request.POST.get('comment_text', None)

        application = models.HackerApplication.objects.get(pk=request.POST.get('app_id'))
        try:
            if request.POST.get('skip'):
                add_vote(application, request.user, None, None)
            elif request.POST.get('add_comment'):
                add_comment(application, request.user, comment_text)
            elif request.POST.get('set_dubious'):
                application.set_dubious()
            elif request.POST.get('unset_dubious'):
                application.unset_dubious()
            else:
                add_vote(application, request.user, tech_vote, pers_vote)
        # If application has already been voted -> Skip and bring next
        # application
        except IntegrityError:
            pass
        return HttpResponseRedirect(reverse('review'))

    def can_vote(self):
        return True


class InviteTeamListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, TemplateView):
    template_name = 'invite_list.html'
    table_class = AdminTeamListTable
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=APP_PENDING) \
            .exclude(user__team__team_code__isnull=True).values('user__team__team_code').order_by() \
            .annotate(vote_avg=Avg('vote__calculated_vote'),
                      team=F('user__team__team_code'),
                      members=Count('user', distinct=True))

    def get_context_data(self, **kwargs):
        c = super(InviteTeamListView, self).get_context_data(**kwargs)
        c.update({'teams': True})
        return c

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.HackerApplication.objects.filter(user__team__team_code__in=ids).all()
        mails = []
        errors = 0
        for app in apps:
            try:
                app.invite(request.user)
                m = emails.create_invite_email(app, request)
                mails.append(m)
            except ValidationError:
                errors += 1
        if mails:
            send_batch_emails(mails)
            messages.success(request, "%s applications invited" % len(mails))
        else:
            errorMsg = "No applications invited"
            if errors != 0:
                errorMsg = "%s applications not invited" % errors
            messages.error(request, errorMsg)

        return HttpResponseRedirect(reverse('invite_teams_list'))


class DubiousApplicationsListView(TabsViewMixin, IsOrganizerMixin, ExportMixin, SingleTableMixin, FilterView):
    template_name = 'dubious_list.html'
    table_class = DubiousListTable
    filterset_class = DubiousApplicationFilter
    table_pagination = {'per_page': 100}
    exclude_columns = ('status', 'vote_avg')
    export_name = 'dubious_applications'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=APP_DUBIOUS)


class _OtherApplicationsListView(TabsViewMixin, IsOrganizerMixin, ExportMixin, SingleTableMixin, FilterView):
    template_name = 'applications_list.html'
    table_pagination = {'per_page': 100}
    exclude_columns = ('detail', 'status')
    export_name = 'applications'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(_OtherApplicationsListView, self).get_context_data(**kwargs)
        context['otherApplication'] = True
        list_email = ""
        for u in self.object_list.values('user__email'):
            list_email += "%s, " % u['user__email']
        context['emails'] = list_email
        return context


class VolunteerApplicationsListView(_OtherApplicationsListView):
    table_class = VolunteerListTable
    filterset_class = VolunteerFilter

    def get_queryset(self):
        return models.VolunteerApplication.objects.all()


class SponsorApplicationsListView(_OtherApplicationsListView):
    table_class = SponsorListTable
    filterset_class = SponsorFilter

    def get_queryset(self):
        return models.SponsorApplication.objects.all()


class MentorApplicationsListView(_OtherApplicationsListView):
    table_class = MentorListTable
    filterset_class = MentorFilter

    def get_queryset(self):
        return models.MentorApplication.objects.all()


class ReviewVolunteerApplicationView(TabsViewMixin, IsOrganizerMixin, TemplateView):
    template_name = 'other_application_detail.html'

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.VolunteerApplication.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('app_id')
        application = models.VolunteerApplication.objects.get(pk=id_)
        if request.POST.get('invite') and request.user.check_is_organizer:
            application.invite(request.user)
            application.save()
        elif request.POST.get('noinvite') and request.user.check_is_organizer:
            application.reject(request)
            application.save()

        return HttpResponseRedirect(reverse('volunteer_detail', kwargs={'id': application.uuid_str}))

    def get_back_url(self):
        return reverse('volunteer_list')

    def get_context_data(self, **kwargs):
        context = super(ReviewVolunteerApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context['app'] = application
        return context


class ReviewSponsorApplicationView(TabsViewMixin, IsOrganizerMixin, TemplateView):
    template_name = 'other_application_detail.html'

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.SponsorApplication.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def get_back_url(self):
        return reverse('sponsor_list')

    def get_context_data(self, **kwargs):
        context = super(ReviewSponsorApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context['app'] = application
        return context


class ReviewMentorApplicationView(TabsViewMixin, IsOrganizerMixin, TemplateView):
    template_name = 'other_application_detail.html'

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.MentorApplication.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('app_id')
        application = models.MentorApplication.objects.get(pk=id_)
        if request.POST.get('invite') and request.user.check_is_organizer:
            application.invite(request.user)
            application.save()
        elif request.POST.get('noinvite') and request.user.check_is_organizer:
            application.reject(request)
            application.save()

        return HttpResponseRedirect(reverse('mentor_detail', kwargs={'id': application.uuid_str}))

    def get_back_url(self):
        return reverse('mentor_list')

    def get_context_data(self, **kwargs):
        context = super(ReviewMentorApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context['app'] = application
        return context
