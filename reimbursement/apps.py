from __future__ import unicode_literals

from django.apps import AppConfig


class ReimbursementConfig(AppConfig):
    name = 'reimbursement'

    def ready(self):
        super(ReimbursementConfig, self).ready()
        from .signals import reimbursement_create
        reimbursement_create
