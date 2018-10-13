from django.contrib import admin
from baggage import models


class BaggageRoomAdmin(admin.ModelAdmin):
    list_display = (
        'room', 'row', 'col', 'door_row', 'door_col'
    )
    search_fields = (
        'room',
    )

    def get_actions(self, request):
        return []


class BaggageListAdmin(admin.ModelAdmin):
    list_display = (
        'bid', 'owner', 'status', 'btype', 'color', 'description', 'special', 'time', 'updated'
    )
    search_fields = (
        'owner__email', 'owner__name', 'status', 'btype', 'color', 'description'
    )
    list_filter = (
        'status', 'btype', 'color', 'special'
    )

    def get_actions(self, request):
        return []


admin.site.register(models.Room, admin_class=BaggageRoomAdmin)
admin.site.register(models.Bag, admin_class=BaggageListAdmin)
