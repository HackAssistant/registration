from checkin import models
from django.contrib import admin


# Register your models here.

class CheckinAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'application', 'update_time'
    )
    search_fields = list_display
    date_hierarchy = 'update_time'


admin.site.register(models.CheckIn, admin_class=CheckinAdmin)
