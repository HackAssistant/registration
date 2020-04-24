from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from applications import models

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'votes', 'reimb', 'status',
                    'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'reimb', 'graduation_year',
                   'university', 'origin', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email',
                     'description',)
    ordering = ('submission_date',)
    date_hierarchy = 'submission_date'

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
        return models.HackerApplication.annotate_vote(qs)


class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'status', 'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'graduation_year',
                   'university', 'origin', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email', 'description',)
    ordering = ('submission_date',)
    date_hierarchy = 'submission_date'

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    name.admin_order_field = 'user__name'  # Allows column order sorting
    name.short_description = 'Volunteer info'  # Renames column head

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def get_queryset(self, request):
        qs = super(VolunteerApplicationAdmin, self).get_queryset(request)
        return models.VolunteerApplication.objects.all()


class MentorApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'status', 'status_last_updated', 'diet')
    list_filter = ('status', 'first_timer', 'graduation_year',
                   'university', 'origin', 'under_age', 'diet')
    list_per_page = 200
    search_fields = ('user__name', 'user__email', 'description',)
    ordering = ('submission_date',)
    date_hierarchy = 'submission_date'

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    name.admin_order_field = 'user__name'  # Allows column order sorting
    name.short_description = 'Volunteer info'  # Renames column head

    def status_last_updated(self, app):
        if not app.status_update_date:
            return None
        return timesince(app.status_update_date)

    status_last_updated.admin_order_field = 'status_update_date'

    def get_queryset(self, request):
        qs = super(MentorApplicationAdmin, self).get_queryset(request)
        return models.MentorApplication.objects.all()


class DraftApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')
    list_per_page = 200
    search_fields = ('user__name', 'user__email',)
    ordering = ('user__name',)

    def name(self, obj):
        return obj.user.get_full_name() + ' (' + obj.user.email + ')'

    def get_queryset(self, request):
        qs = super(DraftApplicationAdmin, self).get_queryset(request)
        return models.DraftApplication.objects.all()


admin.site.register(models.HackerApplication, admin_class=ApplicationAdmin)
admin.site.register(models.VolunteerApplication, admin_class=VolunteerApplicationAdmin)
admin.site.register(models.DraftApplication, admin_class=DraftApplicationAdmin)
admin.site.register(models.MentorApplication, admin_class=MentorApplicationAdmin)
admin.site.site_header = '%s Admin' % settings.HACKATHON_NAME
admin.site.site_title = '%s Admin' % settings.HACKATHON_NAME
admin.site.index_title = 'Home'
admin.site.login = login_required(admin.site.login)
