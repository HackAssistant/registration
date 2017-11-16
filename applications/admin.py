import logging

from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince

from app import slack
from app.slack import SlackInvitationException
from applications import models, emails

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'votes', 'scholarship', 'status',
                    'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'scholarship', 'graduation_year',
                   'university', 'origin_country', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email',
                     'description',)
    ordering = ('submission_date',)
    actions = ['invite', 'ticket', 'invite_slack', 'reject']

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    name.admin_order_field = 'user__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def votes(self, app):
        return app.vote_avg

    votes.admin_order_field = 'vote_avg'

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def get_queryset(self, request):
        qs = super(ApplicationAdmin, self).get_queryset(request)
        return models.Application.annotate_vote(qs)

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)

        if not settings.SLACK.get('team', None) or not settings.SLACK.get('token', None):
            if 'invite_slack' in actions:
                del actions['invite_slack']

        return actions

    def ticket(self, request, queryset):
        sent = 0
        errors = 0
        msgs = []
        for app in queryset:
            try:
                app.confirm()
                msgs.append(emails.create_confirmation_email(app, request))
                sent += 1
            except ValidationError:
                errors += 1

        connection = mail.get_connection()
        connection.send_messages(msgs)
        if sent > 0 and errors > 0:
            self.message_user(request, (
                "%s applications confirmed, %s invites cancelled. Did you "
                "check that they were accepted before?" % (
                    sent, errors)), level=messages.INFO)
        elif sent > 0:
            self.message_user(request, '%s applications confirmed' % sent)
        else:
            self.message_user(request, 'Tickets couldn\'t be sent! Did you '
                                       'check that they were invited?', level=messages.ERROR)

    def invite(self, request, queryset):
        invited = 0
        errors = 0
        msgs = []
        for app in queryset:
            try:
                app.invite(request.user)
                msgs.append(emails.create_invite_email(app, request))
                invited += 1
            except ValidationError:
                errors += 1
        if msgs:
            connection = mail.get_connection()
            connection.send_messages(msgs)
        if invited > 0 and errors > 0:
            self.message_user(request, (
                "%s applications invited, %s invites cancelled. Did you check "
                "that they were accepted before?" % (
                    invited, errors)), level=messages.INFO)
        elif invited > 0:
            self.message_user(request, '%s applications invited' % invited)
        else:
            self.message_user(request, 'Invites couldn\'t be sent! Did you '
                                       'check that they were accepted before?',
                              level=messages.ERROR)

    def reject(self, request, queryset):
        if not request.user.has_perm('register.reject'):
            self.message_user(request, "You don't have permission to reject "
                                       "users")
            return
        rejected = 0
        errors = 0
        for app in queryset:
            try:
                app.reject(request)
                rejected += 1
            except ValidationError:
                errors += 1
        if rejected > 0 and errors > 0:
            self.message_user(request, (
                "%s applications rejected, %s errors. Did you check that they "
                "haven't already attended?" % (
                    rejected, errors)), level=messages.INFO)
        elif rejected > 0:
            self.message_user(request, '%s applications rejected' % rejected)
        else:
            self.message_user(request, 'Are you kidding me? They already '
                                       'attended!',
                              level=messages.ERROR)

    def invite_slack(self, request, queryset):
        invited = 0
        errors = 0
        for app in queryset:
            if app.status in [models.APP_CONFIRMED, models.APP_ATTENDED]:
                try:
                    slack.send_slack_invite(app.user.email)
                    invited += 1
                except SlackInvitationException as e:
                    logging.error(e)
                    errors += 1
            else:
                errors += 1
        if invited > 0 and errors > 0:
            self.message_user(request, (
                "%s applications invited to slack, %s skipped. Have they "
                "confirmed already?" % (invited, errors)), level=messages.INFO)
        elif invited > 0:
            self.message_user(request, '%s applications invited to slack' %
                              invited)
        else:
            self.message_user(request, 'Invites couldn\'t be sent! Did you '
                                       'check that they were confirmed before?',
                              level=messages.ERROR)


admin.site.register(models.Application, admin_class=ApplicationAdmin)
admin.site.site_header = '%s Admin' % settings.HACKATHON_NAME
admin.site.site_title = '%s Admin' % settings.HACKATHON_NAME
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
