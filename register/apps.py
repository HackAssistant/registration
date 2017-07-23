from __future__ import unicode_literals

from django.apps import AppConfig


class RegisterConfig(AppConfig):
    name = 'register'

    def ready(self):
        super(RegisterConfig, self).ready()
        from register.signals import organizer_account, default_site
