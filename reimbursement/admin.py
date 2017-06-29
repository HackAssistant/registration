from django.contrib import admin
# Register your models here.
from django.core import mail
from django.utils.timesince import timesince

from reimbursement import models, emails


class ReimbursementAdmin(admin.ModelAdmin):
    list_display = (
        'application', 'name', 'assigned_money', 'origin', 'status', 'status_last_updated', 'application_status')
    list_filter = ('status', 'reimbursed_by', 'origin_country', 'reimbursed_by', 'application__status')
    list_per_page = 200

    # search_fields = ('hacker__name', 'hacker__lastname', 'hacker__user__email', 'description', 'id')
    ordering = ('creation_date',)
    actions = ['send', ]

    def name(self, obj):
        return obj.application.hacker.name + ' ' + obj.application.hacker.lastname + ' (' + obj.application.hacker.user.email + ')'

    name.admin_order_field = 'application__hacker__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def application_status(self, obj):
        return obj.application.get_status_display()

    application_status.admin_order_field = 'application__status'  # Allows column order sorting

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
            self.message_user(request, "You don't have permission to send reimbursements")
            return
        msgs = []
        sent = 0
        for reimb in queryset:
            reimb.send(request.user)

            msgs.append(emails.create_reimbursement_email(reimb, request))
            sent += 1

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.message_user(request, '%s reimbursements sent' % sent)


admin.site.register(models.Reimbursement, admin_class=ReimbursementAdmin)
