from urllib.parse import quote

import csv
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.base import View, TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework import viewsets, permissions
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin

from app.mixins import TabsViewMixin
from app.utils import reverse
from discord.discord_api import get_token, get_user_id, DISCORD_URL
from discord.form import SwagForm
from discord.models import DiscordUser
from discord.serializers import DiscordSerializer
from discord.tables import DiscordTable, DiscordFilter
from teams.models import Team
from user.mixins import IsHackerMixin, IsOrganizerMixin


def discord_tabs(user):
    return [('Discord list', reverse('discord_list'), False),
            ('Sticker list', reverse('sticker_list'), False), ]


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
        error = request.GET.get('error', None)
        if not error:
            code = request.GET.get('code', None)
            url = request.build_absolute_uri(reverse('discord_redirect'))
            token = get_token(code, url)
            discord_json = get_user_id(token)
            discord_id = discord_json.get('id')
            discord_username = discord_json.get('username')
            discord = DiscordUser(user=request.user, discord_id=discord_id, discord_username=discord_username)
            try:
                team = Team.objects.get(user=request.user)
                discord.team_name = team.team_code
            except Team.DoesNotExist:
                pass
            try:
                discord.save()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'director_button': self.request.user.is_director,
        })
        return context

    def get_current_tabs(self):
        return discord_tabs(self.request.user)

    def get_queryset(self):
        return DiscordUser.objects.select_related('user')


class RedirectError(TemplateView):
    template_name = 'discord_connect_error.html'


class SwagView(IsHackerMixin, TemplateView):
    template_name = 'swag_address_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discord = get_object_or_404(DiscordUser, user=self.request.user)
        form = SwagForm(instance=discord)
        context.update({
            'form': form,
        })
        return context

    def post(self, request, *args, **kwargs):
        discord = get_object_or_404(DiscordUser, user=request.user)
        form = SwagForm(request.POST, instance=discord)
        if form.is_valid():
            form.save()
            messages.success(request, 'Swag info saved!')
            return HttpResponseRedirect(reverse('dashboard'))
        context = self.get_context_data()
        context.update({
            'form': form,
        })
        return render(request, self.template_name, context)


class DiscordStickerList(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, TemplateView):
    template_name = 'discord_list.html'
    table_class = DiscordTable
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return discord_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sticker = self.request.GET.get('sticker', '')
        discords = DiscordUser.objects.select_related('user').exclude(stickers='')
        stickers = set()
        for discord in discords:
            for stick in discord.stickers.split('-'):
                stickers.add(stick)
        context.update({
            'sticker_selected': sticker,
            'sticker_list': stickers,
        })
        return context

    def get_queryset(self):
        sticker = self.request.GET.get('sticker', '')
        discords = DiscordUser.objects.select_related('user')
        if sticker:
            discords = discords.filter(stickers__contains=sticker)
        else:
            discords = discords.exclude(stickers='')
        return discords


def get_csv_address(request):
    if not request.user.is_authenticated or not request.user.is_director:
        raise PermissionDenied()
    response = HttpResponse(
        content_type='text/csv'
    )

    writer = csv.writer(response)
    discord_users = DiscordUser.objects.filter(swag=True, checked_in=True)
    for user in discord_users:
        writer.writerow([user.user.email, user.user.name, user.user.get_type_display(), user.address, user.stickers,
                         user.user.application.origin])
    return response
