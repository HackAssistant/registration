from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.db.models import Avg

from app.utils import export_as_csv_action
from register import models, emails

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']

admin.site.disable_action('delete_selected')


class ApplicationInline(admin.StackedInline):
    model = models.Application
    fields = ('status',)


class HackerAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'lastname')
    inlines = [ApplicationInline, ]
    # list_filter = ('status', 'first_timer', 'scholarship', 'hacker__university', 'hacker__country', 'under_age')
    list_per_page = 200
    # search_fields = ('hacker__name', 'hacker__lastname', 'hacker__user__email', 'description', 'id')
    # ordering = ('submission_date',)
    # actions = ['reject_application', 'invite',
    #            export_as_csv_action(fields=EXPORT_CSV_FIELDS)]


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'votes', 'status')
    list_filter = ('status', 'first_timer', 'scholarship', 'hacker__university', 'origin_country', 'under_age')
    list_per_page = 200
    search_fields = ('hacker__name', 'hacker__lastname', 'hacker__user__email', 'description', 'id')
    ordering = ('submission_date',)
    actions = ['reject_application', 'invite', 'ticket',
               export_as_csv_action(fields=EXPORT_CSV_FIELDS)]

    def name(self, obj):
        return obj.hacker.name + ' ' + obj.hacker.lastname

    name.admin_order_field = 'hacker__name'  # Allows column order sorting
    name.short_description = 'Hacker name'  # Renames column head

    def votes(self, app):
        return app.vote_avg

    votes.admin_order_field = 'vote_avg'

    def get_queryset(self, request):
        qs = super(ApplicationAdmin, self).get_queryset(request)
        return qs.annotate(vote_avg=Avg('vote__calculated_vote'))

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        if not request.user.has_perm('register.invite'):
            if 'invite' in actions: del actions['invite']
            if 'ticket' in actions: del actions['ticket']

        return actions

    def ticket(self, request, queryset):
        if not request.user.has_perm('register.invite'):
            self.message_user(request, "You don't have permission to invite users")
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
                "%s applications confirmed, %s invites cancelled. Did you check that they were accepted before?" % (
                    sent, errors)),
                              level=messages.INFO)
        elif sent > 0:
            self.message_user(request, '%s applications confirmed' % sent)
        else:
            self.message_user(request, 'Tickets couldn\'t be sent! Did you check that they were invited?',
                              level=messages.ERROR)

    def invite(self, request, queryset):
        if not request.user.has_perm('register.invite'):
            self.message_user(request, "You don't have permission to invite users")
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

        connection = mail.get_connection()
        connection.send_messages(msgs)
        if invited > 0 and errors > 0:
            self.message_user(request, (
                "%s applications invited, %s invites cancelled. Did you check that they were accepted before?" % (
                    invited, errors)),
                              level=messages.INFO)
        elif invited > 0:
            self.message_user(request, '%s applications invited' % invited)
        else:
            self.message_user(request, 'Invites couldn\'t be sent! Did you check that they were accepted before?',
                              level=messages.ERROR)

    def reject_application(self, request, queryset):
        # TODO: Move logic to model
        if queryset.exclude(status='P'):
            self.message_user(request, 'Applications couldn\'t be updated, check that they are pending before',
                              messages.ERROR)
        else:
            # Same as above
            models.Application.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='R')
            count = queryset.count()
            self.message_user(request, '%s applications rejected' % count)

    reject_application.short_description = 'Reject'


# class InvitationAdmin(ApplicationAdmin):
#     list_display = (
#         'id', 'name', 'email', 'country', 'scholarship', 'reimbursement_money', 'pending_since', 'last_reminder_sent',
#         'status',
#     )
#     ordering = ('invitation_date',)
#     # Why aren't these overriding super actions?
#     actions = ['update_applications', 'reject_application', 'send_reminder', 'send_reimbursement',
#                export_as_csv_action(fields=EXPORT_CSV_FIELDS)]
#
#     def get_actions(self, request):
#         actions = super(ApplicationAdmin, self).get_actions(request)
#         # Remove some unnecessary actions
#         del actions['update_applications']
#         del actions['accept_application']
#         return actions
#
#     def last_reminder_sent(self, app):
#         if not app.last_reminder:
#             return None
#         return timesince(app.last_reminder)
#
#     last_reminder_sent.admin_order_field = 'last_reminder'
#
#     def pending_since(self, app):
#         if not app.invitation_date:
#             return None
#         return timesince(app.invitation_date)
#
#     pending_since.admin_order_field = 'invitation_date'
#
#     def send_reminder(self, request, queryset):
#         sent = 0
#         errors = 0
#         for app in queryset:
#             try:
#                 app.send_reminder(request)
#                 sent += 1
#             except ValidationError:
#                 errors += 1
#
#         if sent > 0 and errors > 0:
#             self.message_user(request, (
#                 "%s reminders sent, %s reminders cancelled" % (
#                     sent, errors)),
#                               level=messages.WARNING)
#         elif sent > 0:
#             self.message_user(request, '%s reminders sent' % sent)
#         else:
#             self.message_user(request, 'Reminders couldn\'t be sent!', level=messages.ERROR)
#
#     def send_reimbursement(self, request, queryset):
#         sent = 0
#         errors = 0
#         for app in queryset:
#             try:
#                 app.send_reimbursement(request)
#                 sent += 1
#             except ValidationError:
#                 errors += 1
#
#         if sent > 0 and errors > 0:
#             self.message_user(request, (
#                 "%s reimbursement sent, %s reimbursement cancelled" % (
#                     sent, errors)),
#                               level=messages.WARNING)
#         elif sent > 0:
#             self.message_user(request, '%s reimbursements sent' % sent)
#         else:
#             self.message_user(request, 'Reimbursements couldn\'t be sent!',
#                               level=messages.ERROR)
#
#     def get_queryset(self, request):
#         return self.model.objects.filter(status__in=[models.APP_INVITED, models.APP_CONFIRMED, models.APP_ATTENDED])


admin.site.register(models.Application, admin_class=ApplicationAdmin)
admin.site.register(models.Hacker, admin_class=HackerAdmin)
# create_modeladmin(InvitationAdmin, name='invitation', model=models.Application)
admin.site.site_header = 'HackUPC Admin'
admin.site.site_title = 'HackUPC Admin'
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
