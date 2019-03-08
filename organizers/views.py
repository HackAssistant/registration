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
from applications.models import APP_PENDING
from organizers import models
from organizers.tables import ApplicationsListTable, ApplicationFilter, AdminApplicationsListTable, RankingListTable, \
    AdminTeamListTable, InviteFilter, ApplicationTable
from teams.models import Team
from user.mixins import IsOrganizerMixin, IsDirectorMixin, IsExternalMixin
from user.models import User


def add_vote(application, user, tech_rat, pers_rat, passion_rat, culture_rat):
    v = models.Vote()
    v.user = user
    v.application = application

    v.tech = tech_rat
    v.personal = pers_rat
    v.passion = passion_rat
    v.culture = culture_rat

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
    t = [('Applications', reverse('app_list'), False)]
    if user.is_organizer:
        t.append(('Review', reverse('review'), 'new' if models.Application.objects.exclude(vote__user_id=user.id).filter(status=APP_PENDING) else ''))
        t.append(('Ranking', reverse('ranking'), False))
    if user.is_director:
        t.append(('Invite', reverse('invite_list'), False))
        t.append(('Waitlist', reverse('waitlist_list'), False))
        t.append(('Export', reverse('export'), False))
    return t


def recalc(request):
    for app in models.Application.objects.all():
        for vote in models.Vote.objects.filter(application=app):
            vote.save()
    return HttpResponseRedirect(reverse('app_list'))


class RankingView(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'ranking.html'
    table_class = RankingListTable

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return User.objects.annotate(
            vote_count=Count('vote__calculated_vote')).exclude(vote_count=0)


class ApplicationsListView(TabsViewMixin, IsExternalMixin, ExportMixin, SingleTableMixin, FilterView):
    template_name = 'applications_list.html'
    table_class = ApplicationsListTable
    filterset_class = ApplicationFilter
    table_pagination = {'per_page': 100}
    exclude_columns = ('detail', 'status', 'vote_avg')
    export_name = 'applications'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.all())


class ApplicationsExportView(TabsViewMixin, IsOrganizerMixin, ExportMixin, SingleTableMixin, FilterView):
    template_name = 'export.html'
    table_class = ApplicationTable
    filterset_class = ApplicationFilter
    exclude_columns = ('detail',)
    export_name = 'applications'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.all())


class InviteListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, FilterView):
    template_name = 'invite_list.html'
    table_class = AdminApplicationsListTable
    filterset_class = InviteFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.filter(status=APP_PENDING))

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.Application.objects.filter(pk__in=ids).all()
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


class WaitlistListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, FilterView):
    template_name = 'waitlist_list.html'
    table_class = AdminApplicationsListTable
    filterset_class = InviteFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.filter(status=APP_PENDING))

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.Application.objects.filter(pk__in=ids).all()
        mails = []
        errors = 0
        for app in apps:
            try:
                app.reject(request)
                m = emails.create_reject_email(app, request)
                mails.append(m)
            except ValidationError:
                errors += 1
        if mails:
            send_batch_emails(mails)
            messages.success(request, "%s applications wait listed" % len(mails))
        else:
            errorMsg = "No applications wait listed"
            if errors != 0:
                errorMsg = "%s applications not wait listed" % errors
            messages.error(request, errorMsg)

        return HttpResponseRedirect(reverse('waitlist_list'))


class ApplicationDetailView(TabsViewMixin, IsExternalMixin, TemplateView):
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

                mate_app = models.Application.objects.filter(user=mate['user']).first()
                if mate_app:
                    mate['app_uuid_str'] = mate_app.uuid_str

        return context

    def can_vote(self):
        return False

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.Application.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('app_id')
        application = models.Application.objects.get(pk=id_)

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
        elif request.POST.get('slack') and request.user.is_organizer:
            self.slack_invite(application)

        return HttpResponseRedirect(reverse('app_detail', kwargs={'id': application.uuid_str}))

    def waitlist_application(self, application):
        try:
            application.reject(self.request)
            messages.success(self.request, "%s application wait listed" % application.user.email)
            m = emails.create_reject_email(application, self.request)
            m.send()
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
        return models.Application.objects \
            .exclude(vote__user_id=self.request.user.id) \
            .filter(status=APP_PENDING) \
            .annotate(count=Count('vote__calculated_vote')) \
            .order_by('count', 'submission_date') \
            .first()

    def get(self, request, *args, **kwargs):
        r = super(ReviewApplicationView, self).get(request, *args, **kwargs)
        return r

    def post(self, request, *args, **kwargs):
        tech_vote = request.POST.get('tech_rat', None)
        pers_vote = request.POST.get('pers_rat', None)
        passion_vote = request.POST.get('passion_rat', None)
        culture_vote = request.POST.get('cult_rat', None)

        comment_text = request.POST.get('comment_text', None)
        application = models.Application.objects.get(pk=request.POST.get('app_id'))
        try:
            if request.POST.get('skip'):
                add_vote(application, request.user, None, None, None, None)
            elif request.POST.get('add_comment'):
                add_comment(application, request.user, comment_text)
            else:
                add_vote(application, request.user, tech_vote, pers_vote, passion_vote, culture_vote)
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
        return models.Application.objects.filter(status=APP_PENDING).exclude(user__team__team_code__isnull=True) \
            .values('user__team__team_code').order_by().annotate(vote_avg=Avg('vote__calculated_vote'),
                                                                 team=F('user__team__team_code'),
                                                                 members=Count('user', distinct=True))

    def get_context_data(self, **kwargs):
        c = super(InviteTeamListView, self).get_context_data(**kwargs)
        c.update({'teams': True})
        return c

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.Application.objects.filter(user__team__team_code__in=ids).all()
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


class WaitlistTeamListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, TemplateView):
    template_name = 'waitlist_list.html'
    table_class = AdminTeamListTable
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.objects.filter(status=APP_PENDING).exclude(user__team__team_code__isnull=True) \
            .values('user__team__team_code').order_by().annotate(vote_avg=Avg('vote__calculated_vote'),
                                                                 team=F('user__team__team_code'),
                                                                 members=Count('user', distinct=True))

    def get_context_data(self, **kwargs):
        c = super(WaitlistTeamListView, self).get_context_data(**kwargs)
        c.update({'teams': True})
        return c

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('selected')
        apps = models.Application.objects.filter(user__team__team_code__in=ids).all()
        mails = []
        errors = 0
        for app in apps:
            try:
                app.reject(request)
                m = emails.create_reject_email(app, request)
                mails.append(m)
            except ValidationError:
                errors += 1
        if mails:
            send_batch_emails(mails)
            messages.success(request, "%s applications wait listed" % len(mails))
        else:
            errorMsg = "No applications wait listed"
            if errors != 0:
                errorMsg = "%s applications not wait listed" % errors
            messages.error(request, errorMsg)

        return HttpResponseRedirect(reverse('waitliste_teams_list'))
