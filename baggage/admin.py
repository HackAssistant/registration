from django.contrib import admin
from baggage import models

class BaggageListAdmin(admin.ModelAdmin):
    list_display = (
        'owner', 'status', 'type', 'color', 'description', 'special'
    )
    readonly_fields = (
        'time', 'updated'
    )
    search_fields = list_display

    def get_actions(self, request):
        return []


class BaggageCommentAdmin(admin.ModelAdmin):
    list_display = (
        'item', 'time', 'user', 'comment'
    )
    search_fields = list_display

    def get_actions(self, request):
        return []


admin.site.register(models.Bag, admin_class=BaggageListAdmin)
admin.site.register(models.Comment, admin_class=BaggageCommentAdmin)