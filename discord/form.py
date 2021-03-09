from django import forms
from django.core.exceptions import ValidationError

from discord.models import DiscordUser

SWAG_BOOLEAN = (
        ('Yes', True),
        ('No', False)
    )


class SwagForm(forms.ModelForm):
    swag = forms.TypedChoiceField(
        required=True,
        label='This edition we can send swag to your house. Would you want it?',
        coerce=lambda x: x,
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    def clean_address(self):
        address = self.cleaned_data.get('address', '')
        swag = self.cleaned_data.get('swag', False)
        if swag and not address:
            raise ValidationError("If you want swag, please fill your address!")
        return address

    class Meta:
        model = DiscordUser
        fields = ('swag', 'address')
        labels = {
            'address': 'Please specify all your address information so we will be able to send it to you '
                       '(We won\'t send swag to some countries)'
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 5}),
        }
