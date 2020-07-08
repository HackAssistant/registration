from django.contrib import admin

from offer.models import Offer, Code


class OfferAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "codes",)


class CodeAdmin(admin.ModelAdmin):
    list_display = ("id", "offer", "user", "code",)
    ordering = ("id",)


admin.site.register(Offer, admin_class=OfferAdmin)
admin.site.register(Code, admin_class=CodeAdmin)
