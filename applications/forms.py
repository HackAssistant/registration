from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from app.utils import validate_url
from applications import models


class ApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
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
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+#########'}))
    university = forms.CharField(required=True,
                                 label='What university do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your major/degree?',
                             help_text='Current or most recent degree you\'ve received',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    first_timer = forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    reimb = forms.TypedChoiceField(
        required=False,
        label='Do you need a travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    under_age = forms.TypedChoiceField(
        required=True,
        label='How old are you?',
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, '18 or over'), (True, 'Between 14 (included) and 18')),
        widget=forms.RadioSelect
    )

    terms_and_conditions = forms.BooleanField(
        required=False,
        label='I’ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
              'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
              'Privacy and Cookies Policy</a>.<span style="color: red; font-weight: bold;"> *</span>' % (
                  settings.HACKATHON_NAME, settings.HACKATHON_NAME
              )
    )

    cvs_edition = forms.BooleanField(
        required=False,
        label='I authorize "Hackers at UPC" to share my CV with HackUPC 2019 Sponsors.'
    )

    diet_notice = forms.BooleanField(
        required=False,
        label='I authorize "Hackers at UPC" to use my food allergies and intolerances information to '
              'manage the catering service only.<span style="color: red; font-weight: bold;"> *</span>'
    )

    resume = forms.FileField(required=True)

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

    def clean_cvs_edition(self):
        cc = self.cleaned_data.get('cvs_edition', False)
        return cc

    def clean_diet_notice(self):
        diet = self.cleaned_data['diet']
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

    def clean_other_diet(self):
        data = self.cleaned_data['other_diet']
        diet = self.cleaned_data['diet']
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_other_gender(self):
        data = self.cleaned_data['other_gender']
        gender = self.cleaned_data['gender']
        if gender == models.GENDER_OTHER and not data:
            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('university', 'degree', 'graduation_year', 'gender', 'other_gender',
                         'phone_number', 'tshirt_size', 'diet', 'other_diet',
                         'under_age', 'lennyface', 'hardware'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects'), }),
            ('Show us what you\'ve built',
             {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'),
              'description': 'Some of our sponsors may use this information for recruitment purposes,'
              'so please include as much as you can.'}),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        r_enabled = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        if r_enabled and deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',),
                                     'description': 'Reimbursement applications are now closed. '
                                                    'Sorry for the inconvenience.',
                                     }))
        elif self.instance.pk and r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',),
                                     'description': 'If you applied for reimbursement, check out the Travel tab. '
                                                    'Email us at %s for any change needed on reimbursements.' %
                                                    settings.HACKATHON_CONTACT_EMAIL,
                                     }))
        elif not r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',)}), )
        else:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'reimb', 'reimb_amount'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('HackUPC Policies', {
                'fields': ('terms_and_conditions', 'diet_notice', 'cvs_edition'),
                'description': '<p style="color: #202326cc;margin-top: 1em;display: block;'
                               'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                               'process your information to organize an awesome hackaton. It '
                               'will also include images and videos of yourself during the event. '
                               'Your data will be used for admissions mainly. We may also reach '
                               'out to you (sending you an e-mail) about other events that we are '
                               'organizing and that are of a similar nature to those previously '
                               'requested by you. For more information on the processing of your '
                               'personal data and on how to exercise your rights of access, '
                               'rectification, suppression, limitation, portability and opposition '
                               'please visit our Privacy and Cookies Policy.</p>'
            }))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this question if you want.',
            'graduation_year': 'What year have you graduated on or when will you graduate',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'hardware': 'Any hardware that you would like us to have. We can\'t promise anything, '
                        'but at least we\'ll try!',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited.'
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

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', ]
