import requests
from django.conf import settings


class SlackInvitationException(BaseException):
    pass


BASE_URL = 'https://{}.slack.com/api/users.admin.invite'


# Inspired by the code in https://github.com/giginet/django-slack-invitation

def send_slack_invite(email, active=True):
    token = settings.SLACK.get('token', None)
    team = settings.SLACK.get('team', None)

    if not token or not team:
        raise SlackInvitationException(
            "Not configured slack, team = %s and token = %s" % (team, token))

    r = requests.post(BASE_URL.format(team), data={
        'email': email,
        'token': token,
        'set_active': active
    })
    response_object = r.json()
    if r.status_code == 200 and response_object['ok']:
        return True
    else:
        raise SlackInvitationException(response_object['error'])
