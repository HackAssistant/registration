from django.contrib import admin
from meals import models


class MealsMealAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'times', 'starts', 'ends'
    )
    search_fields = (
        'name',
    )

    def get_actions(self, request):
        return []


class MealsEatenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'meal', 'user', 'time'
    )
    search_fields = (
        'name', 'user__name', 'user__email'
    )
    list_filter = (
        'meal', 'user'
    )

    def get_actions(self, request):
        return []


admin.site.register(models.Meal, admin_class=MealsMealAdmin)
admin.site.register(models.Eaten, admin_class=MealsEatenAdmin)
