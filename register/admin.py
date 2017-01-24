from django.contrib import admin
# Register your models here.
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.utils.timesince import timesince
from register import models
from register.models import APP_INVITED
from register.utils import export_as_csv_action, create_modeladmin
from register.forms import ApplicationsTypeform

admin.site.disable_action('delete_selected')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lastname', 'email', 'votes', 'status')
    list_filter = ('status', 'first_timer', 'scholarship', 'university', 'country')
    list_per_page = 200
    search_fields = ('name', 'lastname', 'email')
    ordering = ('submission_date',)
    actions = ['update_applications', 'accept_application', 'reject_application', 'invite',
               export_as_csv_action(fields=['name', 'lastname', 'university', 'country'])]

    def votes(self, app):
        return app.vote_avg

    votes.admin_order_field = 'vote_avg'

    def get_queryset(self, request):
        qs = super(ApplicationAdmin, self).get_queryset(request)
        return qs.annotate(vote_avg=Avg('vote__calculated_vote'))

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        user = request.user
        if not user.has_perm('register.invite_application') and 'invite' in actions:
            del actions['invite']

        return actions

    def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
        # Inspired in: https://gist.github.com/vero4karu/d028f7c1f76563a06b8e
        readonly_fields = [field.name for field in self.opts.local_fields]
        if 'status' in readonly_fields:
            readonly_fields.remove('status')
        return readonly_fields

    def invite(self, request, queryset):
        invited = 0
        errors = 0
        for app in queryset:
            try:
                app.invite(request)
                invited += 1
            except ValidationError:
                errors += 1

        if invited > 0 and errors > 0:
            self.message_user(request, (
                "%s applications invited, %s invites cancelled. Did you check that they were accepted before?" % (
                    invited, errors)),
                              level=messages.WARNING)
        elif invited > 0:
            self.message_user(request, '%s applications invited' % invited)
        else:
            self.message_user(request, 'Invites couldn\'t be sent! Did you check that they were accepted before?',
                              level=messages.ERROR)

    invite.short_description = 'Invite selected applications to HackUPC'

    def update_applications(self, request, queryset):
        count = len(ApplicationsTypeform().update_forms())
        self.message_user(request, 'Added %s applications' % count)

    update_applications.short_description = 'Fetch new applications from Typeform'

    def accept_application(self, request, queryset):
        if queryset.exclude(status='P').exists():
            self.message_user(request, 'Applications couldn\'t be updated, check that they are pending before',
                              messages.ERROR)
        else:
            # We have to use this because queryset has been anotated
            # See: http://stackoverflow.com/questions/13559944/how-to-update-a-queryset-that-has-been-annotated
            models.Application.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='A')
            count = queryset.count()
            self.message_user(request, '%s applications accepted' % count)

    accept_application.short_description = 'Accept selected applications'

    def reject_application(self, request, queryset):
        if queryset.exclude(status='P'):
            self.message_user(request, 'Applications couldn\'t be updated, check that they are pending before',
                              messages.ERROR)
        else:
            # Same as above
            models.Application.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='R')
            count = queryset.count()
            self.message_user(request, '%s applications rejected' % count)

    accept_application.short_description = 'Accept selected applications'


class InvitationAdmin(ApplicationAdmin):
    list_display = ('id', 'name', 'lastname', 'email', 'pending_since')
    ordering = ('invitation_date',)
    # Why aren't these overriding super actions?
    actions = ['update_applications', 'reject_application', 'send_reminder',
               export_as_csv_action(fields=['name', 'lastname', 'university', 'country'])]

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        del actions['invite']
        del actions['update_applications']
        del actions['accept_application']
        return actions

    def pending_since(self, app):
        return timesince(app.invitation_date)

    pending_since.admin_order_field = 'invitation_date'

    def send_reminder(self, request, queryset):
        sent = 0
        errors = 0
        for app in queryset:
            try:
                app.send_reminder(request)
                sent += 1
            except ValidationError:
                errors += 1

        if sent > 0 and errors > 0:
            self.message_user(request, (
                "%s reminders sent, %s reminders cancelled" % (
                    sent, errors)),
                              level=messages.WARNING)
        elif sent > 0:
            self.message_user(request, '%s reminders sent' % sent)
        else:
            self.message_user(request, 'Reminders couldn\'t be sent!',
                              level=messages.ERROR)

    def get_queryset(self, request):
        return self.model.objects.filter(status=APP_INVITED)


admin.site.register(models.Application, admin_class=ApplicationAdmin)
create_modeladmin(InvitationAdmin, name='invitation', model=models.Application)
admin.site.site_header = 'HackUPC Admin'
admin.site.site_title = 'HackUPC Admin'
admin.site.index_title = 'Home'
