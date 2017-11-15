from django import forms
from form_utils.forms import BetterModelForm

from reimbursement.models import Reimbursement, check_friend_emails


class ReimbursementForm(BetterModelForm):
    def __init__(self, *args, **kwargs):
        super(ReimbursementForm, self).__init__(*args, **kwargs)
        self.fields['receipt'].required = True

    def clean_friend_emails(self):
        multipl_hacks = self.cleaned_data.get('friend_emails', '')
        if multipl_hacks:
            try:
                check_friend_emails(multipl_hacks)
            except Exception as e:
                raise forms.ValidationError(e.message)
        return multipl_hacks

    def save(self, commit=True):
        reimb = super(ReimbursementForm, self).save(commit=False)
        reimb.submit_receipt()
        if commit:
            reimb.save()
        return reimb

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

        labels = {
            'multiple_hackers': 'This receipt covers multiple hackers',
            'friend_emails': 'Hackers emails'
        }

        help_texts = {
            'friend_emails': 'Comma separated, use emails your friends used to register'
        }
