from django import forms

from discord.models import DiscordUser

SWAG_BOOLEAN = (
    ('Yes', True),
    ('No', False)
)


class SwagForm(forms.ModelForm):
    swag = forms.TypedChoiceField(
        required=True,
        label='If this edition we can send you swag to your house, would you want it?',
        coerce=lambda x: x,
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address', '')
        swag = cleaned_data.get('swag', 'False')
        if swag == 'True' and address == '':
            self.add_error('address', "If you want swag, please fill your address!")

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
