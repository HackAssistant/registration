import logging

from django.contrib import admin, messages
# Register your models here.
from django.core import mail
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince
from reimbursement import models, emails


class ReimbursementAdmin(admin.ModelAdmin):
    list_display = (
        'application', 'name', 'money', 'origin', 'status',
        'status_last_updated', 'application_status',
        'requested_reimb')
    list_filter = ('status', 'reimbursed_by', 'origin_country',
                   'reimbursed_by', 'application__status')
    list_per_page = 200

    # search_fields = ('hacker__name', 'hacker__lastname',
    # 'hacker__user__email', 'description', 'id')
    ordering = ('creation_date',)
    actions = ['send', ]

    def money(self, obj):
        return str(obj.assigned_money) + obj.currency_sign

    money.admin_order_field = 'assigned_money'

    def name(self, obj):
        hacker = obj.application.hacker
        return hacker.name + ' ' + hacker.lastname + ' (' + hacker.user.email + ')'

    name.admin_order_field = \
        'application__hacker__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def requested_reimb(self, obj):
        return obj.application.scholarship

    requested_reimb.admin_order_field = \
        'application__scholarship'  # Allows column order sorting

    def application_status(self, obj):
        return obj.application.get_status_display()

    application_status.admin_order_field = \
        'application__status'  # Allows column order sorting

    def origin(self, obj):
        return obj.origin_city + ' (' + obj.origin_country + ')'

    origin.admin_order_field = 'origin_city'  # Allows column order sorting

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def send(self, request, queryset):
        if not request.user.has_perm('reimbursement.reimburse'):
            self.message_user(request, "You don't have permission to send "
                                       "reimbursements")
            return
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
