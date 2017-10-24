from __future__ import unicode_literals

from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'

    def ready(self):
        super(UserConfig, self).ready()
        from .signals import user_organizer
        user_organizer
