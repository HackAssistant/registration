from django import forms
from form_utils.forms import BetterModelForm

from reimbursement.models import Reimbursement


class ReimbursementForm(BetterModelForm):
    class Meta:
        model = Reimbursement
        fields = (
            'venmo_user', 'paypal_email', 'receipt', 'multiple_hackers', 'friend_emails', 'origin_city',
            'origin_country')
        fieldsets = (
            ('Upload your receipt',
             {'fields': ('receipt', 'multiple_hackers', 'friend_emails'), }),
            ('Where should we send you the monies?', {'fields': ('venmo_user', 'paypal_email',), }),
            ('Where are you joining us from?', {'fields': ('origin_city', 'origin_country',), }),
        )
        widgets = {
            'origin_country': forms.TextInput(attrs={'autocomplete': 'off'}),
        }
