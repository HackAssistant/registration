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
    phone_number = forms.CharField(required=True, widget=forms.TextInput(
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
        label='Do you need travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    code_conduct = forms.BooleanField(required=False,
                                      label='I have read and accept '
                                            '<a href="%s" target="_blank">%s Code of conduct</a>' % (
                                                getattr(settings, 'CODE_CONDUCT_LINK', '/code_conduct'),
                                                settings.HACKATHON_NAME), )


    privacy_policy = forms.BooleanField(required=False,
                                      label='I have read and accept '
                                            '<a href="%s" target="_blank">%s Privacy Policy</a>' % (
                                                getattr(settings, 'PRIVACY_POLICY_LINK', '/privacy_policy'),
                                                settings.HACKATHON_NAME), )

    application_sharing = forms.BooleanField(
            required=False,
            label='I authorize you to share my application/registration \
            information for event administration, ranking, MLH \
            administration, pre- and post-event informational e-mails, \
            and occasional messages about hackathons in-line with the \
            <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>. \
            I further I agree to the terms of both the \
            <a href="#" target="_blank">MLH Contest Terms and Conditions</a> \
            and the \
            <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>'
        )

    media_permission = forms.BooleanField(
            required=False,
            label='Photos will be taken at the event by the %s \
            organisers and/or by an external party such as MLH. I agree \
            that photos from the event can be taken, used for internal \
            and marketing purposes, shared with our sponsors and partners, \
            including MLH. I also grant %s, MLH and other partners \
            the permission to record and publish photos and video \
            of the event and the exclusive right to produce commercial \
            video content' % (settings.HACKATHON_NAME, settings.HACKATHON_NAME)
        )

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        size = getattr(resume, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume size under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return resume

    def clean_code_conduct(self):
        cc = self.cleaned_data.get('code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must abide by our code of conduct" % settings.HACKATHON_NAME)
        return cc

    def clean_privacy_policy(self):
        pc = self.cleaned_data.get('privacy_policy', False)
        # Check that if it's the first submission hackers checks privacy policy checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not pc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must abide by our privacy policy" % settings.HACKATHON_NAME)
        return pc

    def clean_application_sharing(self):
        aps = self.cleaned_data.get('application_sharing', False)
        # Check if hackers agreed with application sharing
        if not aps and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must give us permission to shre your application" % settings.HACKATHON_NAME)
        return aps

    def clean_media_parmission(self):
        mp = self.cleaned_data.get('media_parmission', False)
        # Check if hackers give us permission to publish media files asociated with them
        if not mp and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must agree with that photos from the event can be used as described below" % settings.HACKATHON_NAME)
        return mp


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
            raise forms.ValidationError("Please fill this in order for us to know you a bit better")
        return data

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

    def clean_other_diet(self):
        data = self.cleaned_data['other_diet']
        diet = self.cleaned_data['diet']
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_other_gender(self):
        data = self.cleaned_data['other_gender']
        gender = self.cleaned_data['gender']
        if gender == 'O' and not data:
            raise forms.ValidationError("Please specify your gender")
        return data

    def clean_other_race(self):
        data = self.cleaned_data['other_race']
        race = self.cleaned_data['race']
        if race == 'O' and not data:
            raise forms.ValidationError("Please specify your race/ethnicity")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('university', 'degree', 'graduation_year', 'gender',
                         'other_gender', 'race', 'other_race', 'phone_number', 'tshirt_size', 'diet',
                         'other_diet', 'birth_day', 'lennyface'),
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
            self._fieldsets.append(('Permissions', 
                {'fields': (
                        'code_conduct',
                        'privacy_policy',
                        'application_sharing',
                        'media_permission',
                    ),
                'description': 'We need this permissions to provide you better experiences'}
            ))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this '
                      'question if you want',
            'race': 'This is just for statistic purposes. You can skip this '
                      'question if you want',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'birth_day': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'tshirt_size': forms.RadioSelect(),
            'graduation_year': forms.RadioSelect(),
        }

        labels = {
            'other_gender': 'What gender do you identify as?',
            'race': 'What is your race/ethnicity?',
            'other_race': 'Please specify your race/ethnicity',
            'graduation_year': 'What is your graduation year?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'birth_day': 'What is your date of birth?',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', 'under_age']
