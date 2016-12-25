from django.contrib import admin
# Register your models here.
from django.core.checks import messages
from django.core.exceptions import ValidationError
from register import models
from register.forms import ApplicationsTypeform

admin.site.disable_action('delete_selected')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lastname', 'email', 'votes', 'test_url', 'status')
    list_filter = ('status', 'first_timer', 'scholarship', 'university')
    search_fields = ('name', 'lastname', 'email')
    ordering = ('-submission_date',)
    actions = ['invite', 'update_applications', 'accept_application']

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        user = request.user
        if not user.has_perm('register.invite_application') and 'invite' in actions:
            del actions['invite']

        return actions

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super(ApplicationAdmin, self).get_fieldsets(request, obj)
        if request.user.has_perm('register.force_status'):
            return (None, {
                'fields': ('status',),
            }),
        return []

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
        if queryset.exclude(status='P'):
            self.message_user(request, 'Applications couldn\'t be updated, check that they are pending before',
                              messages.ERROR)
        else:
            queryset.update(status='A')
            count = queryset.count()
            self.message_user(request, '%s applications accepted' % count)

    accept_application.short_description = 'Accept selected applications'


admin.site.register(models.Application, admin_class=ApplicationAdmin)
