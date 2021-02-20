import django_filters
import django_tables2 as tables
from django.db.models import Q

from discord.models import DiscordUser


class DiscordTable(tables.Table):
    name = tables.Column(accessor='user.name', verbose_name='Name')
    email = tables.Column(accessor='user.email', verbose_name='Email')
    checked_in = tables.Column(accessor='checked_in', verbose_name='On discord')
    team = tables.Column(accessor='team_name', verbose_name='Team')

    class Meta:
        model = DiscordUser
        attrs = {'class': 'table table-hover'}
        template = 'templates/discord_list.html'
        fields = ['name', 'email', 'checked_in', 'team']
        empty_text = 'No users!'


class DiscordFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) |
                               Q(user__name__icontains=value) |
                               Q(team_name__icontains=value))

    class Meta:
        model = DiscordUser
        fields = ['search']
