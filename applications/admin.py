from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from applications import models

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'votes', 'scholarship', 'status',
                    'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'scholarship', 'graduation_year',
                   'university', 'origin_country', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email',
                     'description',)
    ordering = ('submission_date',)

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    name.admin_order_field = 'user__name'  # Allows column order sorting
    name.short_description = 'Hacker info'  # Renames column head

    def votes(self, app):
        return app.vote_avg

    votes.admin_order_field = 'vote_avg'

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def get_queryset(self, request):
        qs = super(ApplicationAdmin, self).get_queryset(request)
        return models.Application.annotate_vote(qs)


admin.site.register(models.Application, admin_class=ApplicationAdmin)
admin.site.site_header = '%s Admin' % settings.HACKATHON_NAME
admin.site.site_title = '%s Admin' % settings.HACKATHON_NAME
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
