from __future__ import unicode_literals

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    name = 'applications'

    def ready(self):
        super(ApplicationsConfig, self).ready()
        from .signals import clean_draftapplication
        clean_draft_application
