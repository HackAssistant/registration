from django.contrib import admin
from baggage import models

class BaggageListAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'owner', 'status', 'type', 'color', 'description', 'special'
    )
    readonly_fields = (
        'time', 'updated'
    )
    search_fields = (
        'owner__email', 'owner__name', 'status', 'type', 'color', 'description'
    )
    list_filter = (
        'status', 'type', 'color', 'special'
    )

    def get_actions(self, request):
        return []


class BaggageCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'item', 'time', 'user', 'comment'
    )
    readonly_fields = (
        'time',
    )
    search_fields = (
        'item__owner__email', 'item__owner__name', 'user__email', 'user__name', 'comment'
    )

    def get_actions(self, request):
        return []


admin.site.register(models.Bag, admin_class=BaggageListAdmin)
admin.site.register(models.Comment, admin_class=BaggageCommentAdmin)