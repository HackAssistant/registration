from django import forms
from django.conf import settings
from django.forms import ModelForm
from django.template.defaultfilters import filesizeformat
from form_utils.forms import BetterModelForm

from reimbursement.models import Reimbursement, check_friend_emails


class ReceiptSubmissionReceipt(BetterModelForm):
    def __init__(self, *args, **kwargs):
        super(ReceiptSubmissionReceipt, self).__init__(*args, **kwargs)
        self.fields['receipt'].required = True

    def clean_friend_emails(self):
        multipl_hacks = self.cleaned_data.get('friend_emails', '')
        if multipl_hacks:
            try:
                check_friend_emails(multipl_hacks, self.instance.hacker.email)
            except Exception as e:
                raise forms.ValidationError(e.message)
        return multipl_hacks

    def clean_paypal_email(self):
        venmo = self.cleaned_data.get('venmo_user', '')
        paypal = self.cleaned_data.get('paypal_email', '')
        if not venmo and not paypal:
            raise forms.ValidationError("Please add either venmo or paypal so we can send you reimbursement")
        return paypal

    def clean_receipt(self):
        receipt = self.cleaned_data['receipt']
        size = getattr(receipt, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return receipt

    def save(self, commit=True):
        reimb = super(ReceiptSubmissionReceipt, self).save(commit=False)
        reimb.submit_receipt()
        if commit:
            reimb.save()
        return reimb

    class Meta:
        model = Reimbursement
        fields = (
            'venmo_user', 'paypal_email', 'receipt', 'multiple_hackers', 'friend_emails', 'origin',)
        fieldsets = (
            ('Upload your receipt',
             {'fields': ('receipt', 'multiple_hackers', 'friend_emails'), }),
            ('From which city are you travelling to %s?' % settings.HACKATHON_NAME, {'fields': ('origin',), }),
            ('Where should we send you the money?', {'fields': ('venmo_user', 'paypal_email',), }),
        )
        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

        labels = {
            'multiple_hackers': 'This receipt covers multiple hackers',
            'friend_emails': 'Hackers emails'
        }

        help_texts = {
            'friend_emails': 'Comma separated, use emails your friends used to register'
        }


class RejectReceiptForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RejectReceiptForm, self).__init__(*args, **kwargs)
        self.fields['public_comment'].required = True

    class Meta:
        model = Reimbursement
        fields = (
            'public_comment',
        )
        labels = {
            'public_comment': 'Why is this receipt being rejected?'
        }


class AcceptReceiptForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AcceptReceiptForm, self).__init__(*args, **kwargs)
        self.fields['reimbursement_money'].required = True

    class Meta:
        model = Reimbursement
        fields = (
            'reimbursement_money', 'origin',)
        labels = {
            'reimbursement_money': 'Total cost in receipt'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
        }


class EditReimbursementForm(ModelForm):
    def __getitem__(self, item):
        item = super(EditReimbursementForm, self).__getitem__(item)
        # Hide reimbursement money if it has not been approved yet!
        if not self.instance.is_accepted() and item.name == 'reimbursement_money':
            item.field.widget = forms.HiddenInput()
        else:
            item.field.required = True
        return item

    class Meta:
        model = Reimbursement
        fields = ('reimbursement_money', 'expiration_time',)
        labels = {
            'reimbursement_money': 'Amount to be reimbursed',
            'expiration_time': 'When is the reimbursement expiring?'
        }
