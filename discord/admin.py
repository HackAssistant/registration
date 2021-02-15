from django.contrib import admin

from discord.models import DiscordUser


class DiscordUserAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'discord_id', 'checked_in'
    )
    search_fields = ('user__email', 'user__name')
    list_filter = ('user',)
    actions = ['delete_selected', ]


admin.site.register(DiscordUser, DiscordUserAdmin)
