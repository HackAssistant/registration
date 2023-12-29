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
        data = self.cleaned_data['other_gender']
        gender = self.cleaned_data['gender']
        if gender == models.GENDER_OTHER and not data:
            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
        return data

    def clean_origin(self):
        origin = self.cleaned_data['origin']
        if origin == "Others":
            origin_verified = origin
        else:
            response = requests.get('https://api.teleport.org/api/cities/', params={'search': origin})
            if response.status_code / 100 != 2:
                if len(origin.split(',')) == 3:
                    return origin
                raise forms.ValidationError("If the dropdown doesn't show up, type following this schema: "
                                            "city, nation, country")
            data = response.json()['_embedded']['city:search-results']
            if not data:
                raise forms.ValidationError("Please select one of the dropdown options or write 'Others'")
            else:
                origin_verified = data[0]['matching_full_name']
        return origin_verified

    def __getitem__(self, name):
        item = super(_BaseApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    class Meta:
        exclude = get_exclude_fields()


# class _HackerMentorVolunteerApplicationForm(OverwriteOnlyModelFormMixin, ModelForm):
#     first_timer = forms.TypedChoiceField(
#         required=True,
#         label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
#         coerce=lambda x: x == 'True',
#         choices=((False, 'No'), (True, 'Yes')),
#         widget=forms.RadioSelect
#     )
#     university = forms.CharField(required=True,
#                                  label='What university do you study at?',
#                                  help_text='Current or most recent school you attended.',
#                                  widget=forms.TextInput(
#                                      attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))
#
#     degree = forms.CharField(required=True, label='What\'s your major/degree?',
#                              help_text='Current or most recent degree you\'ve received',
#                              widget=forms.TextInput(
#                                  attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))
#
#
# class _HackerMentorApplicationForm(OverwriteOnlyModelFormMixin, ModelForm):
#     github = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={'class': 'form-control',
#                'placeholder': 'https://github.com/johnBiene'}))
#     devpost = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={'class': 'form-control',
#                'placeholder': 'https://devpost.com/JohnBiene'}))
#     linkedin = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={'class': 'form-control',
#                'placeholder': 'https://www.linkedin.com/in/john_biene'}))
#     site = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={'class': 'form-control', 'placeholder': 'https://biene.space'}))
#
#     online = forms.TypedChoiceField(
#         required=True,
#         label='How would you like to attend the event: live or online?',
#         initial=False,
#         coerce=lambda x: x == 'True',
#         choices=((False, 'Live'), (True, 'Online')),
#         widget=forms.RadioSelect
#     )
#
#     def clean_resume(self):
#         resume = self.cleaned_data['resume']
#         size = getattr(resume, '_size', 0)
#         if size > settings.MAX_UPLOAD_SIZE:
#             raise forms.ValidationError("Please keep resume size under %s. Current filesize %s" % (
#                 filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
#         return resume
#
#     def clean_github(self):
#         data = self.cleaned_data['github']
#         validate_url(data, 'github.com')
#         return data
#
#     def clean_devpost(self):
#         data = self.cleaned_data['devpost']
#         validate_url(data, 'devpost.com')
#         return data
#
#     def clean_linkedin(self):
#         data = self.cleaned_data['linkedin']
#         validate_url(data, 'linkedin.com')
#         return data
#
#     def clean_projects(self):
#         data = self.cleaned_data['projects']
#         first_timer = self.cleaned_data['first_timer']
#         if not first_timer and not data:
#             raise forms.ValidationError("Please fill this in order for us to know you a bit better.")
#         return data
#
#
#
#
#
#




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
