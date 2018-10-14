import requests
from django.conf import settings
from slackclient import SlackClient


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


def send_slack_message(user_email, content_message):
    botid = settings.SLACK_BOT.get('id', None)
    token = settings.SLACK_BOT.get('token', None)

    if not token:
        print("[ERROR] Slack bot not configured.")
    else:
        sc = SlackClient(token)
        user = sc.api_call('users.lookupByEmail', email=user_email)
        if user["ok"]:
            user_id = user["user"]["id"]
            message = sc.api_call("chat.postMessage", channel=user_id, text=content_message, as_user=botid)
            if not message["ok"]:
                print("[ERROR] Couldn't send Slack message.")
        else:
            print("[ERROR] Couldn't get Slack user information.")
