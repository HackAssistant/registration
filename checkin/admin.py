from django.contrib import admin

from checkin import models


# Register your models here.

class CheckinAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'check_type', 'application', 'update_time'
    )
    search_fields = list_display
    date_hierarchy = 'update_time'

    def get_actions(self, request):
        return []


admin.site.register(models.CheckIn, admin_class=CheckinAdmin)
