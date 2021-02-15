from urllib.parse import quote

from django.conf import settings
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import View

from app.utils import reverse
from discord.discord_api import get_token, get_user_id, DISCORD_URL
from discord.models import DiscordUser
from user.mixins import IsHackerMixin


class ConnectDiscord(IsHackerMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            DiscordUser.objects.get(user=request.user)
            #TODO pag exception
            pass
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
        discord_id = get_user_id(token)
        try:
            DiscordUser(user=request.user, discord_id=discord_id).save()
        except IntegrityError:
            #TODO pag exception
            pass
        return redirect(reverse('dashboard'))
