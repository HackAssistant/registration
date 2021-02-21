from urllib.parse import quote

from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.generic.base import View
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework import viewsets, permissions
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin

from app.mixins import TabsViewMixin
from app.utils import reverse
from discord.discord_api import get_token, get_user_id, DISCORD_URL
from discord.models import DiscordUser
from discord.serializers import DiscordSerializer
from discord.tables import DiscordTable, DiscordFilter
from user.mixins import IsHackerMixin, IsOrganizerMixin


def organizer_tabs(user):
    return [('Discord list', reverse('discord_list'), False), ]


class ConnectDiscord(IsHackerMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            DiscordUser.objects.get(user=request.user)
            return redirect(reverse('alreadyConnected'))
        except DiscordUser.DoesNotExist:
            url = request.build_absolute_uri(reverse('discord_redirect'))
            redirect_uri = quote(url, safe='')
            client_id = getattr(settings, 'DISCORD_CLIENT_ID', '')
            return redirect('%s/oauth2/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=identify' %
                            (DISCORD_URL, client_id, redirect_uri))


class RedirectDiscord(IsHackerMixin, View):

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        url = request.build_absolute_uri(reverse('discord_redirect'))
        token = get_token(code, url)
        discord_json = get_user_id(token)
        discord_id = discord_json.get('id')
        discord_username = discord_json.get('username')
        try:
            DiscordUser(user=request.user, discord_id=discord_id, discord_username=discord_username).save()
        except IntegrityError:
            return redirect(reverse('alreadyConnected'))
        return redirect(reverse('dashboard'))


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = DiscordUser.objects.all()
    serializer_class = DiscordSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.get_serializer().add_related_fields(queryset)
        return queryset


class DiscordTableView(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'discord_list.html'
    table_class = DiscordTable
    filterset_class = DiscordFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return DiscordUser.objects.select_related('user')


class RedirectError(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'discord_connect_error.html')
