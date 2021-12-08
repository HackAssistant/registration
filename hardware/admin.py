from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from hardware import models


class TypeAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        return format_html('<img src="{}" width="200"/>'.format(obj.image.url))

    image_tag.short_description = 'Image'

    list_display = ['name', 'image_tag']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['label', 'item_type', 'comments']


class RequestAdmin(admin.ModelAdmin):
    def remaining_time(self, obj):
        return obj.get_remaining_time()

    remaining_time.short_description = 'Remaining time/Status'
    remaining_time.admin_order_field = 'request_time'

    list_display = ['id', 'item_type', 'user', 'borrowing', 'request_time', 'remaining_time']


class BorrowingAdmin(admin.ModelAdmin):
    def picked_up_time_ago(self, obj):
        return '{} ({} ago)'.format(
            obj.picked_up_time, obj.get_picked_up_time_ago())

    picked_up_time_ago.admin_order_field = 'picked_up_time'

    def returned_time_ago(self, obj):
        if not obj.return_time:
            return "Not returned yet"

        return '{} ({} ago)'.format(
            obj.return_time, obj.get_return_time_ago())

    returned_time_ago.admin_order_field = 'return_time'

    list_display = ['id', 'user', 'item', 'picked_up_time', 'return_time']


admin.site.register(models.ItemType, TypeAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Request, RequestAdmin)
admin.site.register(models.Borrowing, BorrowingAdmin)
