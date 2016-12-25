from django.contrib import admin
# Register your models here.
from django.core.checks import messages
from django.core.exceptions import ValidationError
from register import models


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name','lastname', 'email', 'votes', 'country', 'status')
    list_filter = ('status', 'first_timer', 'schoolarship', 'university')
    search_fields = ('name', 'lastname', 'email')
    actions = ['invite', ]

    def invite(self, request, queryset):
        try:
            [app.invite(request) for app in queryset]
            self.message_user(request, "%s users invited" % queryset.count())
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)

    invite.short_description = 'Invite user in application'


admin.site.register(models.Application, admin_class=ApplicationAdmin)
