from django.contrib import admin
# Register your models here.
from django.core.checks import messages
from django.core.exceptions import ValidationError
from register import models

admin.site.disable_action('delete_selected')


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lastname', 'email', 'votes', 'country', 'status')
    list_filter = ('status', 'first_timer', 'schoolarship', 'university')
    search_fields = ('name', 'lastname', 'email')
    actions = ['invite', ]

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
            self.message_user(request, ("%s applications invited, %s invites cancelled" % invited, errors),
                              level=messages.WARNING)
        elif invited > 0:
            self.message_user(request, '%s applications invited' % invited)
        else:
            self.message_user(request, 'Invites couldn\'t be sent!', level=messages.ERROR)

    invite.short_description = 'Invite selected applications to HackUPC'


admin.site.register(models.Application, admin_class=ApplicationAdmin)
