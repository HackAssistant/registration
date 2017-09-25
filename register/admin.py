import logging

from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.timesince import timesince

from app import slack
from app.slack import SlackInvitationException
from app.utils import reverse
from register import models, emails
from reimbursement import models as r_models

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']

admin.site.disable_action('delete_selected')


class HackerAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name')
    list_filter = ('graduation_year', 'university', 'diet')
    search_fields = ('name', 'lastname', 'user__email',)
    list_per_page = 200

    def full_name(self, obj):
        return obj.name + ' ' + obj.lastname + ' (' + obj.user.email + ')'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('application', 'author', 'text')
    list_per_page = 200
    actions = ['delete_selected', ]


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'votes', 'scholarship', 'status',
                    'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'scholarship', 'hacker__graduation_year',
                   'hacker__university', 'origin_country', 'under_age', 'hacker__diet')
    list_per_page = 200
    search_fields = ('hacker__name', 'hacker__lastname', 'hacker__user__email',
                     'description', 'id')
    ordering = ('submission_date',)
    actions = ['reject_application', 'invite', 'ticket',
               'create_reimbursement', 'invite_slack', 'reject']

    def name(self, obj):
        return obj.hacker.name + ' ' + obj.hacker.lastname + ' (' + obj.hacker.user.email + ')'

    name.admin_order_field = 'hacker__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def diet(self, obj):
        ret = obj.hacker.diet
        if obj.hacker.other_diet:
            ret += ' (' + obj.hacker.other_diet + ')'
        return ret

    diet.admin_order_field = 'hacker__diet'  # Allows column order sorting
    diet.short_description = 'Hacker diet'  # Renames column head

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
        if not request.user.has_perm('register.invite'):
            if 'invite' in actions:
                del actions['invite']
            if 'ticket' in actions:
                del actions['ticket']

        if not request.user.has_perm('register.reject'):
            if 'reject' in actions:
                del actions['reject']

        if not request.user.has_perm('reimbursement.reimburse'):
            if 'create_reimbursement' in actions:
                del actions['create_reimbursement']

        if not settings.SLACK.get('team', None) or not settings.SLACK.get('token', None):
            if 'invite_slack' in actions:
                del actions['invite_slack']

        return actions

    def ticket(self, request, queryset):
        if not request.user.has_perm('register.invite'):
            self.message_user(request, "You don't have permission to invite "
                                       "users")
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
        if not request.user.has_perm('register.invite'):
            self.message_user(request, "You don't have permission to invite "
                                       "users")
            return
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
                    slack.send_slack_invite(app.hacker.user.email)
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

    def reject_application(self, request, queryset):
        # TODO: Move logic to model
        if queryset.exclude(status='P'):
            self.message_user(request, 'Applications couldn\'t be updated, '
                                       'check that they are pending before',
                              messages.ERROR)
        else:
            # Same as above
            models.Application.objects.filter(id__in=queryset.values_list(
                'id', flat=True)).update(status='R')
            count = queryset.count()
            self.message_user(request, '%s applications rejected' % count)

    reject_application.short_description = 'Reject'

    def create_reimbursement(self, request, queryset):
        if not request.user.has_perm('reimbursement.reimburse'):
            self.message_user(request, "You don't have permission to create "
                                       "reimbursements")
            return
        for app in queryset:
            reimb = r_models.Reimbursement.objects.get_or_create(
                application=app, origin_city=app.origin_city,
                origin_country=app.origin_country)
            if reimb[1]:
                reimb[0].check_prices()
            reimb[0].save()

        return HttpResponseRedirect(
            reverse('admin:reimbursement_reimbursement_changelist'))


admin.site.register(models.Application, admin_class=ApplicationAdmin)
admin.site.register(models.ApplicationComment, admin_class=CommentAdmin)
admin.site.register(models.Hacker, admin_class=HackerAdmin)
admin.site.site_header = 'HackUPC Admin'
admin.site.site_title = 'HackUPC Admin'
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
