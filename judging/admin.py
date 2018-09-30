from django.contrib import admin

from judging import models


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'desired_prizes', 'description', 'university')
    search_fields = ['title', 'url', 'university', 'desired_prizes',
                     'submitter_first_name', 'submitter_last_name']
    list_per_page = 100


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'challenge', 'main_judge')
    search_fields = ['name', 'challenge', 'main_judge']


class PresentationAdmin(admin.ModelAdmin):
    pass


class PresentationEvaluationAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Project, admin_class=ProjectAdmin)
admin.site.register(models.Challenge, admin_class=ChallengeAdmin)
admin.site.register(models.Room, admin_class=RoomAdmin)
admin.site.register(models.Presentation, admin_class=PresentationAdmin)
admin.site.register(models.PresentationEvaluation, admin_class=PresentationEvaluationAdmin)
