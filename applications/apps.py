from __future__ import unicode_literals

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    name = 'applications'

    def ready(self):
        super(ApplicationsConfig, self).ready()
        from applications.signals import create_draft_application, clean_draft_application, \
            auto_delete_file_on_change, auto_delete_file_on_delete
        create_draft_application
        clean_draft_application
        auto_delete_file_on_change
        auto_delete_file_on_delete
