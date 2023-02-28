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
    diet = forms.ChoiceField(label='Dietary requirements', choices=models.DIETS, required=False)
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


class _HackerMentorVolunteerApplicationForm(OverwriteOnlyModelFormMixin, ModelForm):
    first_timer = forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )
    university = forms.CharField(required=True,
                                 label='What university do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your major/degree?',
                             help_text='Current or most recent degree you\'ve received',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))


class _HackerMentorApplicationForm(OverwriteOnlyModelFormMixin, ModelForm):
    github = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://github.com/johnBiene'}))
    devpost = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://devpost.com/JohnBiene'}))
    linkedin = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://www.linkedin.com/in/john_biene'}))
    site = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://biene.space'}))

    online = forms.TypedChoiceField(
        required=True,
        label='How would you like to attend the event: live or online?',
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, 'Live'), (True, 'Online')),
        widget=forms.RadioSelect
    )

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        size = getattr(resume, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume size under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return resume

    def clean_github(self):
        data = self.cleaned_data['github']
        validate_url(data, 'github.com')
        return data

    def clean_devpost(self):
        data = self.cleaned_data['devpost']
        validate_url(data, 'devpost.com')
        return data

    def clean_linkedin(self):
        data = self.cleaned_data['linkedin']
        validate_url(data, 'linkedin.com')
        return data

    def clean_projects(self):
        data = self.cleaned_data['projects']
        first_timer = self.cleaned_data['first_timer']
        if not first_timer and not data:
            raise forms.ValidationError("Please fill this in order for us to know you a bit better.")
        return data


class HackerApplicationForm(_BaseApplicationForm, _HackerMentorApplicationForm, _HackerMentorVolunteerApplicationForm):
    bootstrap_field_info = {
        'Personal Info': {
            'fields': [{'name': 'university', 'space': 12}, {'name': 'degree', 'space': 12},
                       {'name': 'graduation_year', 'space': 12}, {'name': 'gender', 'space': 12},
                       {'name': 'other_gender', 'space': 12}, {'name': 'phone_number', 'space': 12},
                       {'name': 'tshirt_size', 'space': 12}, {'name': 'under_age', 'space': 12},
                       {'name': 'lennyface', 'space': 12}, ],
            'description': 'Hey there, before we begin we would like to know a little more about you.'
        },
        'Hackathons': {
            'fields': [{'name': 'description', 'space': 12}, {'name': 'first_timer', 'space': 12},
                       {'name': 'projects', 'space': 12}, ]
        },
        'Show us what you\'ve built': {
            'fields': [{'name': 'github', 'space': 12}, {'name': 'devpost', 'space': 12},
                       {'name': 'linkedin', 'space': 12}, {'name': 'site', 'space': 12},
                       {'name': 'resume', 'space': 12}, ],
            'description': 'Some of our sponsors may use this information for recruitment purposes,'
                           'so please include as much as you can.'
        }
    }

    reimb = forms.TypedChoiceField(
        required=False,
        label='Do you need a travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect()
    )

    cvs_edition = forms.BooleanField(
        required=False,
        label='I authorize "Hackers at UPC" to share my CV with HackUPC 2023 Sponsors.'
    )

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        self.fields['resume'].required = True

    def clean_cvs_edition(self):
        cc = self.cleaned_data.get('cvs_edition', False)
        return cc

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        size = getattr(resume, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume size under %s. Current filesize %s!" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        if not resume and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to provide a resume."
            )
        return resume

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

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        # Fieldsets ordered and with description
        discord = getattr(settings, 'DISCORD_HACKATHON', False)
        hardware = getattr(settings, 'HARDWARE_ENABLED', False)
        hybrid = getattr(settings, 'HYBRID_HACKATHON', False)
        personal_info_fields = fields['Personal Info']['fields']
        personal_info_fields.append({'name': 'online', 'space': 12})
        if not hybrid:
            self.fields['online'].widget = forms.HiddenInput()
        polices_fields = [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'cvs_edition', 'space': 12},
                          {'name': 'email_subscribe', 'space': 12}]
        if not discord:
            personal_info_fields.extend([{'name': 'diet', 'space': 12}, {'name': 'other_diet', 'space': 12}, ])
            polices_fields.append({'name': 'diet_notice', 'space': 12})
        if hardware:
            personal_info_fields.append({'name': 'hardware', 'space': 12})
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        r_enabled = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        if r_enabled and deadline and deadline <= timezone.now() and not self.instance.pk:
            fields['Traveling'] = {'fields': [{'name': 'origin', 'space': 12}, ],
                                   'description': 'Reimbursement applications are now closed. '
                                                  'Sorry for the inconvenience.',
                                   }
        elif self.instance.pk and r_enabled:
            fields['Traveling'] = {'fields': [{'name': 'origin', 'space': 12}, ],
                                   'description': 'If you applied for reimbursement, check out the Travel tab. '
                                                  'Email us at %s for any change needed on reimbursements.' %
                                                  settings.HACKATHON_CONTACT_EMAIL,
                                   }
        elif not r_enabled:
            fields['Traveling'] = {'fields': [{'name': 'origin', 'space': 12}, ], }
        else:
            fields['Traveling'] = {'fields': [{'name': 'origin', 'space': 12}, {'name': 'reimb', 'space': 12},
                                              {'name': 'reimb_amount', 'space': 12}, ], }

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            fields['HackUPC Policies'] = {
                'fields': polices_fields,
                'description': '<p style="color: margin-top: 1em;display: block;'
                               'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                               'process your information to organize an awesome hackathon. It '
                               'will also include images and videos of yourself during the event. '
                               'Your data will be used for admissions mainly. We may also reach '
                               'out to you (sending you an e-mail) about other events that we are '
                               'organizing and that are of a similar nature to those previously '
                               'requested by you. For more information on the processing of your '
                               'personal data and on how to exercise your rights of access, '
                               'rectification, suppression, limitation, portability and opposition '
                               'please visit our Privacy and Cookies Policy.</p>'}
        return fields

    class Meta(_BaseApplicationForm.Meta):
        model = models.HackerApplication
        extensions = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this question if you want.',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'hardware': 'Any hardware that you would like us to have. We can\'t promise anything, '
                        'but at least we\'ll try!',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited',
            'resume': 'Accepted file formats: %s' % (', '.join(extensions) if extensions else 'Any'),
            'origin': "Please select one of the dropdown options or write 'Others'. If the dropdown doesn't show up,"
                      " type following this schema: <strong>city, nation, country</strong>"
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'hardware': 'Hardware you would like us to have',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),
        }


class VolunteerApplicationForm(_BaseApplicationForm, _HackerMentorVolunteerApplicationForm):
    first_time_volunteer = forms.TypedChoiceField(
        required=True,
        label='Is it your first time volunteering in %s?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((True, 'Yes'), (False, 'No')),
        widget=forms.RadioSelect
    )
    which_hack = forms.MultipleChoiceField(
        required=False,
        label='Which %s editions have you volunteered in?' % settings.HACKATHON_NAME,
        widget=forms.CheckboxSelectMultiple,
        choices=models.PREVIOUS_HACKS
    )
    night_shifts = forms.TypedChoiceField(
        required=False,
        label='Would you be okay with doing night shifts?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes'), (None, 'Maybe')),
        widget=forms.RadioSelect
    )
    university = forms.CharField(initial='NA', widget=forms.HiddenInput(), required=False)
    degree = forms.CharField(initial='NA', widget=forms.HiddenInput(), required=False)

    bootstrap_field_info = {
        'Personal Info': {
            'fields': [{'name': 'under_age', 'space': 12}, {'name': 'gender', 'space': 12},
                       {'name': 'other_gender', 'space': 12}, {'name': 'origin', 'space': 12}],
            'description': 'Hey there, we need some information before we start :)'
        },
        'Volunteering': {
            'fields': [{'name': 'first_time_volunteer', 'space': 12}, {'name': 'which_hack', 'space': 12},
                       {'name': 'english_level', 'space': 12}, {'name': 'attendance', 'space': 12},
                       {'name': 'volunteer_motivation', 'space': 12}, ],
        },
        'Some other questions': {
            'fields': [{'name': 'friends', 'space': 12}, {'name': 'night_shifts', 'space': 12},
                       {'name': 'tshirt_size', 'space': 12}],
            'description': 'Don’t panic! There are just a few more questions 🤯'
        },
        'Personal Interests': {
            'fields': [{'name': 'fav_movie', 'space': 12}, {'name': 'quality', 'space': 12},
                       {'name': 'weakness', 'space': 12}, {'name': 'hobbies', 'space': 12},
                       {'name': 'cool_skill', 'space': 12},
                       # Hidden
                       {'name': 'graduation_year', 'space': 12}, {'name': 'university', 'space': 12},
                       {'name': 'degree', 'space': 12}, {'name': 'first_timer', 'space': 12},
                       {'name': 'lennyface', 'space': 12}, ],
            'description': 'We want to get to know you!'
        }
    }

    def clean(self):
        data = self.cleaned_data['which_hack']
        volunteer = self.cleaned_data['first_time_volunteer']
        if volunteer and not data:
            self.add_error('which_hack', "Choose the hackathons you volunteered")

        return super(VolunteerApplicationForm, self).clean()

    def volunteer(self):
        return True

    def clean_reimb_amount(self):
        data = self.cleaned_data['reimb_amount']
        reimb = self.cleaned_data.get('reimb', False)
        if reimb and not data:
            raise forms.ValidationError("To apply for reimbursement please set a valid amount")
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

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, 'DISCORD_HACKATHON', False)
        other_fields = fields['Some other questions']['fields']
        polices_fields = [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'email_subscribe', 'space': 12}]
        if not discord:
            other_fields.extend([{'name': 'diet', 'space': 12}, {'name': 'other_diet', 'space': 12}, ])
            polices_fields.append({'name': 'diet_notice', 'space': 12})
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            fields['HackUPC Policies'] = {
                'fields': polices_fields,
                'description': '<p style="color: margin-top: 1em;display: block;'
                               'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                               'process your information to organize an awesome hackathon. It '
                               'will also include images and videos of yourself during the event. '
                               'Your data will be used for admissions mainly. We may also reach '
                               'out to you (sending you an e-mail) about other events that we are '
                               'organizing and that are of a similar nature to those previously '
                               'requested by you. For more information on the processing of your '
                               'personal data and on how to exercise your rights of access, '
                               'rectification, suppression, limitation, portability and opposition '
                               'please visit our Privacy and Cookies Policy.</p>'}
        return fields

    class Meta(_BaseApplicationForm.Meta):
        model = models.VolunteerApplication
        help_texts = {
            'gender': 'This is for demographic purposes.',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'attendance': "It will be a great experience to enjoy from beginning to end with lots of things to do, "
                          "but it is ok if you can't make it the whole weekend!",
            'english_level': "No English level needed to volunteer, we just want to check which of you would be"
                             " comfortable doing tasks that require communication in English!",
            'fav_movie': 'e.g.: Interstellar, Game of Thrones,  Avatar, La Casa de Papel, etc.',
            'cool_skill': 'The 3 most original will have a small prize to be given',
            'friends': 'Remember that you all have to apply separately',
            'origin': 'We are just checking if you will be in Barcelona from April to May',
            'volunteer_motivation': 'It can be a short answer, we are just curious 😛!'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'english_level': forms.RadioSelect(),
            'friends': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'weakness': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'quality': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'hobbies': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'graduation_year': forms.HiddenInput(),
            'phone_number': forms.HiddenInput(),
            'first_timer': forms.HiddenInput(),
            'lennyface': forms.HiddenInput(),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Do you have any dietary restrictions? ',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin': 'Where are you joining us from?',
            'which_hack': 'Which %s editions have you volunteered in?' % settings.HACKATHON_NAME,
            'attendance': 'Which days will you attend to HackUPC?',
            'english_level': 'What is your English level?',
            'quality': 'Name a quality of yours:',
            'weakness': 'Now a weakness:',
            'cool_skill': 'What is a cool skill or fun fact about you? Surprise us 🎉 ',
            'fav_movie': 'What is your favorite movie or series?',
            'friends': 'Are you applying with some friends? Enter their complete names',
            'hobbies': 'What are your hobbies or what do you do for fun?',
            'volunteer_motivation': 'Why do you want to volunteer at HackUPC?'
        }


class MentorApplicationForm(_BaseApplicationForm, _HackerMentorApplicationForm, _HackerMentorVolunteerApplicationForm):
    first_time_mentor = forms.TypedChoiceField(
        required=True,
        label='Have you participated as mentor in past HackUPC editions?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect)

    study_work = forms.TypedChoiceField(
        required=True,
        label='Are you studying or working?',
        coerce=lambda x: x == 'True',
        choices=((False, 'Working'), (True, 'Studying')),
        widget=forms.RadioSelect)

    company = forms.CharField(required=False,
                              help_text='Backend developer, DevOps…',
                              label='What is your current role?')

    university = forms.CharField(initial='NA', widget=forms.HiddenInput(), required=False)

    degree = forms.CharField(required=False, label='What\'s your major/degree of study?',
                             help_text='Current or most recent degree you\'ve received',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    graduation_year = forms.ChoiceField(required=False, choices=models.YEARS,
                                        help_text='What year have you graduated on or when will you graduate',
                                        label='What year will you graduate?',
                                        widget=forms.RadioSelect())

    bootstrap_field_info = {
        'Personal Information': {
            'fields': [{'name': 'origin', 'space': 12}, {'name': 'gender', 'space': 12},
                       {'name': 'other_gender', 'space': 12}, {'name': 'tshirt_size', 'space': 12},
                       {'name': 'under_age', 'space': 12}, {'name': 'lennyface', 'space': 12}],
            'description': 'Hey there, before we begin we would like to know a little more about you.'
        },
        'Background information': {
            'fields': [{'name': 'study_work', 'space': 12}, {'name': 'company', 'space': 12},
                       {'name': 'university', 'space': 12}, {'name': 'degree', 'space': 12},
                       {'name': 'graduation_year', 'space': 12}, {'name': 'english_level', 'space': 12},
                       {'name': 'fluent', 'space': 12}, {'name': 'experience', 'space': 12},
                       {'name': 'linkedin', 'space': 12}, {'name': 'site', 'space': 12},
                       {'name': 'github', 'space': 12}, {'name': 'devpost', 'space': 12},
                       {'name': 'resume', 'space': 12}, ],
        },
        'Hackathons': {
            'fields': [{'name': 'why_mentor', 'space': 12}, {'name': 'first_timer', 'space': 12},
                       {'name': 'first_time_mentor', 'space': 12}, {'name': 'which_hack', 'space': 12},
                       {'name': 'participated', 'space': 12}, {'name': 'attendance', 'space': 12}, ],
        },
    }

    def mentor(self):
        return True

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, 'DISCORD_HACKATHON', False)
        hybrid = getattr(settings, 'HYBRID_HACKATHON', False)
        personal_info_fields = fields['Personal Information']['fields']
        polices_fields = [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'email_subscribe', 'space': 12}]
        personal_info_fields.append({'name': 'online', 'space': 12})
        if not hybrid:
            self.fields['online'].widget = forms.HiddenInput()
        if not discord:
            personal_info_fields.extend([{'name': 'diet', 'space': 12}, {'name': 'other_diet', 'space': 12}, ])
            polices_fields.append({'name': 'diet_notice', 'space': 12})
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            fields['HackUPC Policies'] = {
                'fields': polices_fields,
                'description': '<p style="color: margin-top: 1em;display: block;'
                               'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                               'process your information to organize an awesome hackathon. It '
                               'will also include images and videos of yourself during the event. '
                               'Your data will be used for admissions mainly. We may also reach '
                               'out to you (sending you an e-mail) about other events that we are '
                               'organizing and that are of a similar nature to those previously '
                               'requested by you. For more information on the processing of your '
                               'personal data and on how to exercise your rights of access, '
                               'rectification, suppression, limitation, portability and opposition '
                               'please visit our Privacy and Cookies Policy.</p>'}
        return fields

    def clean(self):
        data = self.cleaned_data['which_hack']
        mentor = self.cleaned_data['first_time_mentor']
        if mentor and not data:
            self.add_error('which_hack', "Choose the hackathons you mentored")
        study = self.cleaned_data['study_work']
        if study:
            if not self.cleaned_data['university']:
                self.add_error('university', 'Type your university, please')
            if not self.cleaned_data['degree']:
                self.add_error('degree', 'Type your degree, please')
            if not self.cleaned_data['graduation_year']:
                self.add_error('graduation_year', 'Choose your graduation year, please')
        else:
            self.cleaned_data['graduation_year'] = models.DEFAULT_YEAR
            if not self.cleaned_data['company']:
                self.add_error('company', 'Type your company, please')

        return super(MentorApplicationForm, self).clean()

    class Meta(_BaseApplicationForm.Meta):
        model = models.MentorApplication
        extensions = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

        help_texts = {
            'gender': 'This is for demographic purposes.',
            # 'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'participated': 'You can talk about about past hackathons or any other events. ',
            'resume': 'Accepted file formats: %s' % (', '.join(extensions) if extensions else 'Any'),
            'fluent': 'Catalan, French, Chinese, Arabic…',
            'experience': 'C++, Java, Docker, Vue, AWS…'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'participated': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
            'english_level': forms.RadioSelect(),
            'fluent': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'experience': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'why_mentor': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'first_timer': forms.HiddenInput(),
            'resume': forms.HiddenInput(),
            'lennyface': forms.HiddenInput(),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What is your t-shirt size?',
            'diet': 'Dietary requirements',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'participated': 'Have you participated as mentor in other hackathons or tech events?',
            'resume': 'Upload your resume',
            'why_mentor': 'Why do you want to participate as mentor?',
            'which_hack': 'Which editions have you mentored?',
            'attendance': 'Which days will you be attending HackUPC?',
            'english_level': 'How confident are you speaking in English?',
            'fluent': 'What languages do you speak?',
            'experience': 'What technologies/programming languages do you know?'
        }


class SponsorForm(OverwriteOnlyModelFormMixin, BootstrapFormMixin, ModelForm):
    diet = forms.ChoiceField(required=False, choices=models.DIETS)
    tshirt_size = forms.ChoiceField(required=False, choices=models.TSHIRT_SIZES)
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+#########'}))
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

    bootstrap_field_info = {
        'Personal Info': {
            'fields': [{'name': 'name', 'space': 12}, {'name': 'email', 'space': 12},
                       {'name': 'phone_number', 'space': 12},
                       {'name': 'tshirt_size', 'space': 12}, {'name': 'diet', 'space': 12},
                       {'name': 'other_diet', 'space': 12}, {'name': 'position', 'space': 12},
                       {'name': 'attendance', 'space': 12}],
            'description': 'Hey there, before we begin we would like to know a little more about you.'
        },
    }

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

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, 'DISCORD_HACKATHON', False)
        personal_info_fields = fields['Personal Info']['fields']
        polices_fields = [{'name': 'terms_and_conditions', 'space': 12}, ]
        if not discord:
            personal_info_fields.extend([{'name': 'diet', 'space': 12}, {'name': 'other_diet', 'space': 12}, ])
            polices_fields.append({'name': 'diet_notice', 'space': 12})
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        fields['HackUPC Policies'] = {
            'fields': polices_fields,
            'description': '<p style="color: margin-top: 1em;display: block;'
                           'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                           'process your information to organize an awesome hackathon. It '
                           'will also include images and videos of yourself during the event. '
                           'Your data will be used for admissions mainly. We may also reach '
                           'out to you (sending you an e-mail) about other events that we are '
                           'organizing and that are of a similar nature to those previously '
                           'requested by you. For more information on the processing of your '
                           'personal data and on how to exercise your rights of access, '
                           'rectification, suppression, limitation, portability and opposition '
                           'please visit our Privacy and Cookies Policy.</p>'}
        return fields

    class Meta:
        model = models.SponsorApplication
        help_texts = {
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'email': 'This is needed in order to invite you to our message service'
        }
        labels = {
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'attendance': 'What availability will you have during the event?',
            'position': 'What is your job position?',
        }
        exclude = ['user', 'uuid', 'submission_date', 'status_update_date', 'status', ]
