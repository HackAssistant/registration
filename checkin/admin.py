from django.contrib import admin

from checkin import models


# Register your models here.

class CheckinAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'type', 'application', 'update_time'
    )
    search_fields = ('user__email', 'user__name', 'hacker__user__name', 'hacker__user__email', 'volunteer__user__name',
                     'volunteer__user__email', 'mentor__user__name', 'mentor__user__email', 'sponsor__user__name',
                     'sponsor__user__email')
    date_hierarchy = 'update_time'
    list_filter = ('user', )
    actions = ['delete_selected', ]


admin.site.register(models.CheckIn, admin_class=CheckinAdmin)
