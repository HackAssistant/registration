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
    list_display = ('project', 'room', 'done', 'score', 'tech_score',
                    'learning_score', 'design_score', 'ux_score', 'smoke_score')
    list_filter = ('room__challenge', 'room', 'done')

    def score(self, presentation):
        return presentation.score_avg

    score.admin_order_field = 'score_avg'

    def tech_score(self, presentation):
        return presentation.tech_avg

    def design_score(self, presentation):
        return presentation.design_avg

    def ux_score(self, presentation):
        return presentation.ux_avg

    def smoke_score(self, presentation):
        return presentation.smoke_avg

    tech_score.admin_order_field = 'tech_score'

    def design_score(self, presentation):
        return presentation.design_avg

    design_score.admin_order_field = 'design_score'

    def learning_score(self, presentation):
        return presentation.learning_avg

    learning_score.admin_order_field = 'learning_score'

    def completion_score(self, presentation):
        return presentation.completion_avg

    completion_score.admin_order_field = 'completion_score'

    def get_queryset(self, request):
        qs = super(PresentationAdmin, self).get_queryset(request)
        return models.Presentation.annotate_score(qs)


class PresentationEvaluationAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Project, admin_class=ProjectAdmin)
admin.site.register(models.Challenge, admin_class=ChallengeAdmin)
admin.site.register(models.Room, admin_class=RoomAdmin)
admin.site.register(models.Presentation, admin_class=PresentationAdmin)
admin.site.register(models.PresentationEvaluation, admin_class=PresentationEvaluationAdmin)
