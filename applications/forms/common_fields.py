
from django import forms
from django.conf import settings

def common_first_timer():
    return forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )


def common_university():
    return forms.CharField(
        required=True,
        label='What university do you study at?',
        help_text='Current or most recent school you attended.',
        widget=forms.TextInput(
        attrs={'class': 'typeahead-schools', 'autocomplete': 'off'})
    )


def common_degree():
    return forms.CharField(
        required=True,
        label='What\'s your major/degree?',
        help_text='Current or most recent degree you\'ve received',
        widget=forms.TextInput(
        attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'})
    )



def social_media_field(field_name, placeholder):
    return forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': placeholder}
        ),
        label=field_name.capitalize()
    )


def common_online():
    return forms.TypedChoiceField(
        required=True,
        label='How would you like to attend the event: live or online?',
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, 'Live'), (True, 'Online')),
        widget=forms.RadioSelect
    )
