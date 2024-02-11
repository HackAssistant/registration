from django import forms
from django.conf import settings
from django.core.validators import URLValidator


def common_first_timer():
    return forms.TypedChoiceField(
        required=True,
        label="Will %s be your first hackathon?" % settings.HACKATHON_NAME,
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
    )


def common_university():
    return forms.CharField(
        required=True,
        label="What university do you study at?",
        help_text="Current or most recent school you attended.",
        widget=forms.TextInput(
            attrs={"class": "typeahead-schools", "autocomplete": "off"}
        ),
    )


def common_degree():
    return forms.CharField(
        required=True,
        label="What's your major/degree?",
        help_text="Current or most recent degree you've received",
        widget=forms.TextInput(
            attrs={"class": "typeahead-degrees", "autocomplete": "off"}
        ),
    )


# class CustomURLValidator(URLValidator):
#     message = "Please enter a valid URL"


def social_media_field(field_name, placeholder):
    if field_name == "website":
        return forms.CharField(
            required=False,
            widget=forms.TextInput(
                attrs={"class": "form-control", "placeholder": placeholder},
                validators=[URLValidator(message="Please enter a valid URL")],
            ),
            label=field_name.capitalize(),
        )
    return forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": placeholder}
        ),
        label=field_name.capitalize(),
    )


def social_required(field_name, placeholder):
    return forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": placeholder}
        ),
        label=field_name.capitalize(),
    )


def common_online():
    return forms.TypedChoiceField(
        required=True,
        label="How would you like to attend the event: live or online?",
        initial=False,
        coerce=lambda x: x == "True",
        choices=((False, "Live"), (True, "Online")),
        widget=forms.RadioSelect,
    )
