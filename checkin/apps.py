from __future__ import unicode_literals

from django.apps import AppConfig


class CheckinConfig(AppConfig):
    name = 'checkin'

    def ready(self):
        super(CheckinConfig, self).ready()

