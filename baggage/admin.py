from django.contrib import admin
from baggage import models

class BaggageListAdmin(admin.ModelAdmin):
    list_display = (
        'owner', 'active', 'type', 'color', 'description', 'special'
    )
    search_fields = list_display

    def get_actions(self, request):
        return []


class BaggageMoveAdmin(admin.ModelAdmin):
    list_display = (
        'item', 'time', 'type'
    )
    search_fields = list_display

    def get_actions(self, request):
        return []


admin.site.register(models.Bag, admin_class=BaggageListAdmin)
admin.site.register(models.Move, admin_class=BaggageMoveAdmin)