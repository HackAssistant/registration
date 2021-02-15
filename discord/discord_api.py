import requests
from django.conf import settings

DISCORD_URL = 'https://discord.com/api/v8'


def get_token(code, redirect_uri):
    secret_id = getattr(settings, 'DISCORD_SECRET_ID', '')
    client_id = getattr(settings, 'DISCORD_CLIENT_ID', '')
    data = {
        'client_id': client_id,
        'client_secret': secret_id,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'scope': 'identify email connections'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % DISCORD_URL, data=data, headers=headers)
    r.raise_for_status()
    return r.json().get('access_token')


def get_user_id(token):
    headers = {
        'Authorization': 'Bearer %s' % token
    }
    r = requests.get('%s/users/@me' % DISCORD_URL, headers=headers)
    r.raise_for_status()
    return r.json().get('id')
