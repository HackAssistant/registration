import os 
import json
from django import forms
from django.conf import settings
from django.forms import ModelForm
from django.forms.utils import ErrorList
from django.template.defaultfilters import filesizeformat
from django.utils import timezone

from app.mixins import OverwriteOnlyModelFormMixin, BootstrapFormMixin
from app.utils import validate_url
from applications import models

import requests

from .common_fields import *


def set_field_html_name(cls, new_name):
    """
    This creates wrapper around the normal widget rendering,
    allowing for a custom field name (new_name).
    """
    old_render = cls.widget.render

    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    cls.widget.render = _widget_render_wrapper


def get_exclude_fields():
    discord = getattr(settings, 'DISCORD_HACKATHON', False)
    exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', 'contacted_by',
               'blacklisted_by']
    if discord:
        exclude.extend(['diet', 'other_diet', 'diet_notice'])
    return exclude


class _BaseApplicationForm(OverwriteOnlyModelFormMixin, BootstrapFormMixin, ModelForm):
    diet = forms.ChoiceField(label='Dietary requirements', choices=models.DIETS, required=True)
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+#########'}))
    under_age = forms.TypedChoiceField(
        required=True,
        label='How old will you be at time of the event?',
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, '18 or over'), (True, 'Between 14 (included) and 18')),
        widget=forms.RadioSelect
    )

    terms_and_conditions = forms.BooleanField(
        required=False,
        label='I\'ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
              'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
              'Privacy and Cookies Policy</a>.<span style="color: red; font-weight: bold;"> *</span>' % (
                  settings.HACKATHON_NAME, settings.HACKATHON_NAME
              )
    )

    diet_notice = forms.BooleanField(
        required=False,
        label='I authorize "Hackers at UPC" to use my food allergies and intolerances information to '
              'manage the catering service only.<span style="color: red; font-weight: bold;"> *</span>'
    )

    email_subscribe = forms.BooleanField(required=False, label='Subscribe to our Marketing list in order to inform '
                                                               'you about our next events.')

    def clean_terms_and_conditions(self):
        cc = self.cleaned_data.get('terms_and_conditions', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept our Terms & Conditions and"
                " our Privacy and Cookies Policy."
            )
        return cc

    def clean_diet_notice(self):
        diet = self.cleaned_data.get('diet', 'None')
        diet_notice = self.cleaned_data.get('diet_notice', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if diet != 'None' and not diet_notice and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept us to use your personal data related to your food "
                "allergies and intolerances only in order to manage the catering service."
            )
        return diet_notice

    def clean_other_diet(self):
        data = self.cleaned_data.get('other_diet', '')
        diet = self.cleaned_data.get('diet', 'None')
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_other_gender(self):
        gender = self.cleaned_data.get('gender')
        other_gender = self.cleaned_data.get('other_gender', None)
        if gender == "X" and not other_gender:
            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
        return other_gender

    def clean_origin(self):
        origin = self.cleaned_data['origin']
        # read from json file on local machine

        # actual file path 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        # get static relative path
        STATIC_ROOT = os.path.join(dir_path, "../static")

        # open relative file
        with open(os.path.join(STATIC_ROOT,'cities.json')) as f:
            countries = json.load(f)

            # check if is part of the list
            if origin not in countries:
                raise forms.ValidationError("Please select one of the dropdown options and don't forget to add commas")
            return origin

    def __getitem__(self, name):
        item = super(_BaseApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    class Meta:
        exclude = get_exclude_fields()


class ConfirmationInvitationForm(BootstrapFormMixin, forms.ModelForm):
    bootstrap_field_info = {
        '': {
            'fields': [{'name': 'tshirt_size', 'space': 4}, {'name': 'diet', 'space': 4},
                       {'name': 'other_diet', 'space': 4},
                       {'name': 'reimb', 'space': 12}, {'name': 'reimb_amount', 'space': 12},
                       {'name': 'terms_and_conditions', 'space': 12}, {'name': 'mlh_required_terms', 'space': 12},
                       {'name': 'mlh_required_privacy', 'space': 12}, {'name': 'mlh_subscribe', 'space': 12}
                       ],
        },
    }

    diet = forms.ChoiceField(label='Dietary requirements', choices=models.DIETS, required=True)
    reimb = forms.TypedChoiceField(
        required=False,
        label='Do you need a travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect(),
        help_text='We only provide travel reimbursement if you attend from outside of Catalonia, '
                  'you can find more info in our website\'s FAQ'
    )

    mlh_required_terms = forms.BooleanField(
        label='I have read and agree to the MLH <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">Code of '
              'Conduct</a>. <span style="color: red; font-weight: bold;"> *</span>'
    )

    mlh_subscribe = forms.BooleanField(
        required=False,
        label="I authorize MLH to send me an email where I can further opt into the MLH Hacker, Events, or "
              "Organizer Newsletters and other communications from MLH."
    )

    mlh_required_privacy = forms.BooleanField(
        label="I authorize you to share my application/registration information with Major League Hacking for "
              "event administration, ranking, and MLH administration in-line with the MLH "
              "<a href=\"https://mlh.io/privacy\"></a>. I further agree to the terms of both the MLH Contest "
              "<a href=\"https://github.com/MLH/mlh-policies/blob/main/contest-terms.md\">Terms and Conditions</a> "
              "and the MLH <a href=\"https://mlh.io/privacy\">Privacy Policy</a>. "
              "<span style=\"color: red; font-weight: bold;\"> *</span>"
    )

    terms_and_conditions = forms.BooleanField(
        label='I\'ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
              'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
              'Privacy and Cookies Policy</a>.<span style="color: red; font-weight: bold;"> *</span>' % (
                  settings.HACKATHON_NAME, settings.HACKATHON_NAME
              )
    )

    def clean_mlh_required_terms(self):
        cc = self.cleaned_data.get('mlh_required_terms', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept MLH's Terms & Conditions."
            )
        return cc

    def clean_mlh_required_privacy(self):
        cc = self.cleaned_data.get('mlh_required_privacy', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept MLH's Privacy and Cookies Policy"
            )
        return cc

    def clean_mlh_optional_communications(self):
        cc = self.cleaned_data.get('mlh_optional_communications', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept MLH's mlh_optional_communications"
            )
        return cc

    def clean_other_diet(self):
        data = self.cleaned_data.get('other_diet', '')
        diet = self.cleaned_data.get('diet', 'None')
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_reimb_amount(self):
        data = self.cleaned_data['reimb_amount']
        reimb = self.cleaned_data.get('reimb', False)
        if reimb and not data:
            raise forms.ValidationError("To apply for reimbursement please set a valid amount.")
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if data and deadline and deadline <= timezone.now():
            raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
        return data

    def clean_reimb(self):
        reimb = self.cleaned_data.get('reimb', False)
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if reimb and deadline and deadline <= timezone.now():
            raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
        return reimb

    class Meta:
        model = models.HackerApplication
        fields = ['diet', 'other_diet', 'reimb', 'reimb_amount', 'tshirt_size']
        help_texts = {
            'other_diet': 'If you have any special dietary requirements, please write write them here. '
                          'We want to make sure we have food for you!',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited',
        }
        labels = {
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),
        }
