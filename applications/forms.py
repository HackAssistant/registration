from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm
from django.core.exceptions import ObjectDoesNotExist

from app.mixins import OverwriteOnlyModelFormMixin
from app.utils import validate_url
from applications import models


def calculate_age(born):
    today = timezone.now()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

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

    country = forms.CharField(required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    university = forms.CharField(required=True,
                                 label='What university (or high school) do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    major = forms.CharField(required=False, label='What is your major?',
                             help_text='Your major of study at university (e.g. Computer Science or Mathematics)',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-majors', 'autocomplete': 'off'}))

    degree = forms.CharField(required=False, label='What is your current or most recent level of study?',
                             help_text='Current or most recent degree you\'ve received '
                                       '(e.g. Bachelor\'s or Master\'s degree)',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    hear_about = forms.CharField(
        required=True,
        label='Where did you first hear about %s?' % settings.HACKATHON_NAME,
        widget=forms.TextInput(attrs={'class': 'typeahead-marketing_types', 'autocomplete': 'off'})
    )

    ambassador = forms.CharField(
        required=False,
        label='Do you have a secret code?',
        help_text='This should be blank unless you were told a secret code, in which case enter it here.',
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

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

    visas = forms.TypedChoiceField(
        required=False,
        label='Do you need an Invitation letter for visa?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    code_conduct = forms.BooleanField(required=False,
                                      label='I have read and agree to the '
                                            '<a href="%s" target="_blank">%s MLH Code of Conduct</a>.\
											I further agree to the terms of both the \
											<a href="https://github.com/MLH/mlh-policies/blob/master/prize-terms-and-conditions/contest-terms.md" \
											target="_blank">MLH Contest Terms and Conditions</a> and the \
											<a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>\
                                            <span style="color: red">*</span>' % (
                                                getattr(settings, 'CODE_CONDUCT_LINK', '/code_conduct'),
                                                'MLH'
                                            ))
    privacy_policy = forms.BooleanField(required=False,
                                      label='I have read and accept '
                                            '<a href="%s" target="_blank">%s Privacy Policy</a>\
                                            <span style="color: red">*</span>' % (
                                                getattr(settings, 'PRIVACY_POLICY_LINK', '/privacy_policy'),
                                                settings.HACKATHON_NAME), )
    application_sharing = forms.BooleanField(
            required=False,
            label='I authorize you to share my application/registration information with Major League Hacking for event administration, \
            ranking, MLH administration, and with my authorization email in-line with the <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>\
            <span style="color: red">*</span>'
        )


    data_sharing = forms.BooleanField(required=False,label='I authorize Major League Hacking to send me occasional messages about hackathons.<span style="color: red">*</span>')

    partners_permission = forms.BooleanField(
        required=False,
        label='I authorize you to share my application/registration information, including the CV, '
              'with partners of %s. We, or our partners, may perform processing on and make use of the data '
              'in your application for recruiting purposes, for example, sponsors may send you a job offer. '
              '<span style="color: red">*</span>' % settings.HACKATHON_NAME
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
            video content <span style="color: red">*</span>\
            ' % (settings.HACKATHON_NAME, settings.HACKATHON_NAME)
        )

    guardian_name = forms.CharField(label='Full name of Parent/Legal guardian',
                                    max_length=255, required=False)
    guardian_birth_day = forms.DateField(label='Date of birth of Parent/Legal guardian',
                                         required=False,
                                         widget=forms.DateInput(attrs={'type': 'date'}))
    guardian_code_conduct = forms.BooleanField(required=False,
                                      label='I have read and agree to the '
                                            '<a href="%s" target="_blank">%s MLH Code of Conduct</a>.\
                                            I further agree to the terms of both the \
                                            <a href="https://github.com/MLH/mlh-policies/blob/master/prize-terms-and-conditions/contest-terms.md" \
                                            target="_blank">MLH Contest Terms and Conditions</a> and the \
                                            <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>\
                                            <span style="color: red">*</span>' % (
                                                getattr(settings, 'CODE_CONDUCT_LINK', '/code_conduct'),
                                                'MLH'
                                            ))
    guardian_privacy_policy = forms.BooleanField(required=False,
                                        label='I have read and accept '
                                              '<a href="%s" target="_blank">%s Privacy Policy</a>\
                                              <span style="color: red">*</span>' % (
                                                  getattr(settings, 'PRIVACY_POLICY_LINK', '/privacy_policy'),
                                                  settings.HACKATHON_NAME), )
    guardian_application_sharing = forms.BooleanField(
        required=False,
        label='I authorize you to share application/registration information with Major League Hacking for event administration, \
            ranking, MLH administration, and with atendee\'s authorization email in-line with the <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>\
            <span style="color: red">*</span>'
        )
    
    guardian_partners_permission = forms.BooleanField(
        required=False,
        label='I authorize you to share the application/registration information, including the CV, '
              'with partners of %s. We, or our partners, may perform processing on and make use of the data '
              'in the application for recruiting purposes, for example, sponsors may send the attendee a job offer. '
              '<span style="color: red">*</span>' % settings.HACKATHON_NAME
        )
    guardian_media_permission = forms.BooleanField(
        required=False,
        label='Photos will be taken at the event by the %s \
                organisers and/or by an external party such as MLH. I agree \
                that photos from the event can be taken, used for internal \
                and marketing purposes, shared with our sponsors and partners, \
                including MLH. I also grant %s, MLH and other partners \
                the permission to record and publish photos and video \
                of the event and the exclusive right to produce commercial \
                video content <span style="color: red">*</span>\
                ' % (settings.HACKATHON_NAME, settings.HACKATHON_NAME)
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
                "To attend %s you must give us permission to share your application with MLH" % settings.HACKATHON_NAME)
        return aps

    def clean_data_sharing(self):
        ds = self.cleaned_data.get('data_sharing', False)
        # Check if hackers agreed with data sharing
        if not ds and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must give us permission to share your data with MLH" % settings.HACKATHON_NAME)
        return ds

    def clean_media_permission(self):
        mp = self.cleaned_data.get('media_permission', False)
        # Check if hackers give us permission to publish media files asociated with them
        if not mp and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must agree with that photos from the event can be used as described below" % settings.HACKATHON_NAME)
        return mp


    def clean_partners_permission(self):
        pp = self.cleaned_data.get('partners_permission', False)
        # Check if hackers give us permission to publish media files asociated with them
        if not pp and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must give us permission to share your data with partners of %s" % (settings.HACKATHON_NAME, settings.HACKATHON_NAME))
        return pp


    def is_guardian_required(self):
        applicant_bd = self.cleaned_data.get('birth_day', None)
        if applicant_bd and calculate_age(applicant_bd) < 18:
            return True
        return False

    def clean_guardian_birth_day(self):
        bd = self.cleaned_data.get('guardian_birth_day', None)
        if not self.instance.pk and self.is_guardian_required():
            if not bd:
                raise forms.ValidationError("Please specify your birth day")
            # Check that the guardian is at least 18
            if calculate_age(bd) < 18:
                raise forms.ValidationError("Parent/Legal guardian must be over 18")
        return bd

    def clean_guardian_code_conduct(self):
        cc = self.cleaned_data.get('guardian_code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk and self.is_guardian_required():
            raise forms.ValidationError(
                "As a parent or legal guardian you must abide by our code of conduct")
        return cc

    def clean_guardian_privacy_policy(self):
        pc = self.cleaned_data.get('guardian_privacy_policy', False)
        # Check that if it's the first submission hackers checks privacy policy checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not pc and not self.instance.pk and self.is_guardian_required():
            raise forms.ValidationError(
                "As a parent or legal guardian you must abide by our privacy policy")
        return pc

    def clean_guardian_application_sharing(self):
        aps = self.cleaned_data.get('guardian_application_sharing', False)
        # Check if hackers agreed with application sharing
        if not aps and not self.instance.pk and self.is_guardian_required():
            raise forms.ValidationError(
                "As a parent or legal guardian you must give us permission to share the application with MLH")
        return aps

    def clean_guardian_media_permission(self):
        mp = self.cleaned_data.get('guardian_media_permission', False)
        # Check if hackers give us permission to publish media files asociated with them
        if not mp and not self.instance.pk and self.is_guardian_required():
            raise forms.ValidationError(
                "As a parent or legal guardian you must agree with that photos from the event can be used "
                "as described below")
        return mp

    def clean_guardian_partners_permission(self):
        pp = self.cleaned_data.get('guardian_partners_permission', False)
        # Check if hackers give us permission to publish media files asociated with them
        if not pp and not self.instance.pk and self.is_guardian_required():
            raise forms.ValidationError(
                "As a parent or legal guardian you must give us permission to share the data "
                "with partners of %s" % settings.HACKATHON_NAME)
        return pp


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

    def clean_other_race(self):
        data = self.cleaned_data['other_race']
        race = self.cleaned_data['race']
        if race == 'O' and not data:
            raise forms.ValidationError("Please specify your race/ethnicity")
        return data

    def clean_ambassador(self):
        data = self.cleaned_data['ambassador']
        if data:
            try:
                ambassador = models.Ambassador.objects.get(secret_code=data)
            except(models.Ambassador.DoesNotExist):
                raise forms.ValidationError("Ambassador with this secret code does not exist. \
                Leave blank instead if you don't have ambassador")
            else:
                return ambassador
        else:
            return None

    def clean_job_type(self):
        data = self.cleaned_data['job_type']
        interest = self.cleaned_data['job_interest']
        if not interest == 'No' and not data:
            raise forms.ValidationError("Please specify what type of job do you prefer")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('gender', 'race', 'other_race', 'birth_day',
                         'phone_number', 'country', 'university', 'major', 'degree', 'graduation_year',
                         'tshirt_size', 'diet', 'other_diet'),
             'description': 'Hey there, before we begin, we need to know some basics about you.', }),
            ('Job preferences',
             {'fields': ('job_interest', 'job_type'),
             'description': 'What if our sponsors offers you some job?', }),
            ('Let us get to know you better',
             {'fields': ('spirit_animal',),
             'description': 'We would like to know a little more about you. ;)', }),
            ('Hackathons?', {'fields': ('description', 'hear_about', 'first_timer', 'projects'), }),
            ('Show us what you\'ve built',
             {'fields': ('resume', 'site', 'github', 'devpost', 'linkedin'),
             'description': 'Some of our sponsors may use this information for recruitment purposes, '
             'so please include as much as you can.'}),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        r_enabled = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        if r_enabled and deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'visas',),
                                     'description': 'Reimbursement applications are now closed. '
                                                    'Sorry for the inconvenience.',
                                     }))
        elif self.instance.pk and r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'visas',),
                                     'description': 'If you applied for reimbursement, check out the Travel tab. '
                                                    'Email us at %s for any change needed on reimbursements.' %
                                                    settings.HACKATHON_CONTACT_EMAIL,
                                     }))
        elif not r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'visas',)}), )
        else:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'visas', 'reimb', 'reimb_amount'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        # if not self.instance.pk:
            # self._fieldsets.append(('Secret code', {'fields': ('ambassador',),}))

        self._fieldsets.append(('Other', {'fields': ('comment',),}))

        if not self.instance.pk:
            self._fieldsets.append(
                ('Permissions',
                    {'fields': (
                            'code_conduct',
                            'privacy_policy',
                            'application_sharing',
							'data_sharing',
                            'partners_permission',
                            'media_permission',
                        ),
                        'description': 'We need these permissions to provide you better experience'}),
            )
            self._fieldsets.append(
                ('Permissions of Parent/Legal guardian',
                 {'fields': (
                     'guardian_name',
                     'guardian_birth_day',
                     'guardian_code_conduct',
                     'guardian_privacy_policy',
                     'guardian_application_sharing',
                     'guardian_partners_permission',
                     'guardian_media_permission',
                 ),
                     'description': 'If you are under 18, your parent or legal guardian must agree with the '
                                    'permissions below.<br>The fields below must be filled in by your parent or '
                                    'legal guardian.'}),
            )
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
            'birth_day': 'When you click on the field, you should see a pop-up where you can \
            choose a date.',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'resume': 'Uploading your resume significantly increases your chances of being invited to %s' % settings.HACKATHON_NAME,
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': '<p>' + settings.REIMBURSEMENT_AMOUNTS + '</p><p>'
                            + settings.REIMBURSEMENT_REQUIREMENTS + '</p>',
            'comment': 'If there is anything more you want us to know, put it here (e.g. special needs).'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'birth_day': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'spirit_animal': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'tshirt_size': forms.RadioSelect(),
            'graduation_year': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }

        labels = {
            'comment': 'Do you have any additional comments?',
            'race': 'What is your race/ethnicity?',
            'other_race': 'Please specify your race/ethnicity',
            'graduation_year': 'What is your graduation year?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'birth_day': 'What is your date of birth?',
            'job_interest': 'Are you looking for a job?',
            'job_type': 'What type of job would you prefer?',
            'spirit_animal': 'What\'s your spirit animal and why?',
            'origin': 'From which city are you planning to travel to %s?' % settings.HACKATHON_NAME,
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),
        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', 'under_age']


class AmbassadorForm(OverwriteOnlyModelFormMixin, BetterModelForm):
    university = forms.CharField(required=True,
                                 label='What university (or high school) do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    privacy_policy = forms.BooleanField(required=False,
                                      label='I have read and accept '
                                            '<a href="%s" target="_blank">%s Privacy Policy</a>' % (
                                                getattr(settings, 'PRIVACY_POLICY_LINK', '/privacy_policy'),
                                                settings.HACKATHON_NAME), )

    def clean_privacy_policy(self):
        pc = self.cleaned_data.get('privacy_policy', False)
        # Check that if it's the first submission hackers checks privacy policy checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not pc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must abide by our privacy policy" % settings.HACKATHON_NAME)
        return pc

    def fieldsets(self):
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('origin', 'phone_number', 'university', 'tshirt_size'),
             'description': 'Hey there, before we begin, we need to know some basics about you.', }),
        ]

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Permissions',
                {'fields': (
                        'privacy_policy',
                    ),
                'description': 'We need this permissions to make you our\'s ambassador'}
            ))

        return super(AmbassadorForm, self).fieldsets

    class Meta:
        model = models.Ambassador

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'tshirt_size': forms.RadioSelect(),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+#########'})
        }

        labels = {
            'origin': 'From which city are you planning to travel to %s?' % settings.HACKATHON_NAME,
            'tshirt_size': 'What\'s your t-shirt size?',
        }

        exclude = ['user', 'secret_code', 'created_date']
