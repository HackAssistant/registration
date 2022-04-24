from slack_sdk import WebClient


class SlackManager:
    def __init__(self, token):
        self.client = WebClient(token=token)

    def send_message(self, user, message):
        response = self.client.users_lookupByEmail(email=user.email)
        if not response.data['ok']:
            return False
        user_slack_id = response.data['user']['id']
        response = self.client.conversations_open(users=user_slack_id)
        if not response.data['ok']:
            return False
        channel = response.data['channel']['id']
        self.client.chat_postMessage(channel=channel, text=message)
