from multiprocessing import Pool

from django.conf import settings

from app.patterns import SingletonMeta
from app.services.messages.slack_manager import SlackManager


class MessageManager(metaclass=SingletonMeta):
    def __init__(self):
        self.manager = None
        token = settings.SLACK_BOT.get('token', None)
        if token is not None:
            self.manager = SlackManager(token)

    def send_message(self, *args, **kwargs):
        if self.manager is not None:
            pool = Pool(processes=1)
            pool.apply_async(self.manager.send_message, kwds=kwargs)
