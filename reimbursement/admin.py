import logging

from django.contrib import admin, messages
# Register your models here.
from django.core import mail
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince

from reimbursement import models, emails


class ReimbursementAdmin(admin.ModelAdmin):
    list_display = ('hacker', 'money', 'origin', 'status',
                    'timeleft_expiration', 'application_status',)
    list_filter = ('status', 'origin',
                   'reimbursed_by', 'hacker__application__status')

    search_fields = ['application__user__name', 'application__user__lastname', 'application__user__email',
                     'origin']
    list_per_page = 200

    ordering = ('creation_time',)
    actions = ['send', ]

    def money(self, obj):
        return str(obj.max_assignable_money)

    def name(self, obj):
        user = obj.application.user
        return user.full_name + ' (' + user.email + ')'

    name.admin_order_field = 'hacker__full_name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def application_status(self, obj):
        return obj.hacker.application.get_status_display()

    application_status.admin_order_field = 'hacker__application__status'  # Allows column order sorting

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def send(self, request, queryset):
        msgs = []
        sent = 0
        errors = 0
        for reimb in queryset:
            try:
                reimb.send(request.user)
                msgs.append(emails.create_reimbursement_email(reimb, request))
                sent += 1
            except ValidationError as e:
                errors += 1
                logging.error(e.message)

        if msgs:
            connection = mail.get_connection()
            connection.send_messages(msgs)
        if sent > 0 and errors > 0:
            self.message_user(request, (
                "%s reimbursements sent, %s reimbursements not sent. Did you "
                "check that they were invited before and with money assigned?"
                % (sent, errors)), level=messages.WARNING)
        elif sent > 0:
            self.message_user(request, '%s reimbursement sent' % sent,
                              level=messages.SUCCESS)
        else:
            self.message_user(request,
                              'Reimbursement couldn\'t be sent! Did you check '
                              'that app was invited before and with money '
                              'assigned?',
                              level=messages.ERROR)


admin.site.register(models.Reimbursement, admin_class=ReimbursementAdmin)
