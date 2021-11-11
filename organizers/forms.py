from django import forms
from django.conf import settings

from app.mixins import BootstrapFormMixin


class InviteFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {'fields': [{'name': 'search', 'space': 6}, {'name': 'first_timer', 'space': 2}]}}

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        reimbursement = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        hybrid = getattr(settings, 'HYBRID_HACKATHON', False)
        if reimbursement:
            fields['']['fields'].append({'name': 'reimb', 'space': 2})
        if hybrid:
            fields['']['fields'].append({'name': 'online', 'space': 2})
        return fields
