import requests
from django.conf import settings

from app.utils import reverse


def auth_mlh(auth_code, request):
    conf = settings.OAUTH_PROVIDERS.get('mlh', {})

    # If logic not configured, exit
    if not conf or not conf.get('id', False):
        raise ValueError('Bad configuration, this should never show up')

    # Get Auth code from GET request
    conf['code'] = auth_code
    if not conf['code']:
        raise ValueError('Invalid URL')

    # Get Bearer token
    conf['redirect_url'] = reverse('callback', request=request, kwargs={'provider': 'mlh'})
    token_url = '{token_url}?client_id={id}&client_secret={secret}&code={code}&' \
                'redirect_uri={redirect_url}&grant_type=authorization_code'.format(**conf).replace('\n', '')
    resp = requests.post(
        token_url
    )
    if resp.json().get('error', None):
        raise ValueError('Authentification failed, try again please!')

    # Get access token
    return resp.json().get('access_token', None)


def get_mlh_user(access_token):
    conf = settings.OAUTH_PROVIDERS.get('mlh', {})
    conf['access_token'] = access_token
    mlhuser = requests.get('{user_url}?access_token={access_token}'.format(**conf)).json()
    if mlhuser.get('status', None).lower() != 'ok':
        raise ValueError('Authentification failed, try again please!')
    return mlhuser.get('data', {})
