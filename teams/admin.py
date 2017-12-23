from django.contrib import admin

# Register your models here.
from teams import models


class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_code', 'user',)
    list_per_page = 200
    list_filter = ('team_code', 'user')
    search_fields = ('team_code', 'user')
    actions = ['delete_selected', ]


admin.site.register(models.Team, admin_class=TeamAdmin)
