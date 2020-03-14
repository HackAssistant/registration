from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm
from django.forms.widgets import HiddenInput

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
        choices=((False, '18 or over'), (True, 'Under 18')),
        widget=forms.RadioSelect
    )

    code_conduct = forms.BooleanField(required=False,
                                      label='I have read and accept the '
                                            '<a href="%s" target="_blank">%s Code of Conduct</a>' % (
                                                getattr(settings, 'CODE_CONDUCT_LINK', '/code_conduct'),
                                                settings.HACKATHON_NAME), )

    type = ''

    first_timer_extra = forms.TypedChoiceField(
        required=True,
        label='',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    is_student = forms.TypedChoiceField(
        required=True,
        label='Are you studying or working?',
        coerce=lambda x: x == 'True',
        choices=((False, 'Working'), (True, 'Studying')),
        widget=forms.RadioSelect
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
        if gender == models.GENDER_OTHER and not data:
            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def setType(self, type):
        self.type = type
        self.instance.type = type
        label = ''
        if type == models.VOLUNTEER:
            label = 'volunteered'
            self.fields['weakness'].required = True
            self.fields['quality'].required = True
            self.fields['cool_skill'].required = True
            self.fields['fav_movie'].required = True
            self.fields['origin'].required = False
        elif type == models.MENTOR:
            label = 'mentored'
            self.fields['quality'].required = True
            self.fields['company'].required = True
            self.fields['description'].label = 'Why do you want to participate as mentor?'
            self.fields['quality'].label = 'Which programming languages are you fluent on?'
        elif type == models.SPONSOR:
            self.fields['company'].required = True
        self.fields['first_timer_extra'].label = 'Have you %s to any edition of %s?' % (label, settings.HACKATHON_NAME)

    # noinspection PyTypeChecker
    def __hackerFieldsets(self):
        self._fieldsets.extend((('Hacker Info',
                                 {'fields': ('university', 'degree', 'graduation_year')}),
                                ('Hackathons?',
                                 {'fields': ('description', 'first_timer', 'projects'), }),
                                ('Show us what you\'ve built',
                                 {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'),
                                  'description': 'Some of our sponsors may use this information for recruitment '
                                                 'purposes, '
                                                 'so please include as much as you can.'}),))
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
                                    {'fields': ('origin', 'reimb', 'reimb_amount')}), )

    def __volunteerFieldsets(self):
        self._fieldsets.extend((('Academic Info',
                                 {'fields': ('university', 'degree', 'graduation_year'),
                                  'description': 'Now tell us some information we need for your volunteer application'
                                  }),
                                ('Volunteer Info',
                                 {'fields': ('first_timer', 'first_timer_extra', 'which_hack', 'attendance',
                                             'english_level', 'quality', 'weakness', 'cool_skill', 'fav_movie',
                                             'lennyface', 'friends'),
                                  'description': "Now we're going to ask you some questions about your volunteering "
                                                 "skills."
                                  })
                                ))
        self.fields['origin'].widget = HiddenInput()
        self.fields['description'].widget = HiddenInput()

    def __sponsorFieldsets(self):
        self._fieldsets.append((('Sponsor Info',
                                 {'fields': ('company', 'sponsor_position', 'attendance'),
                                  'description': 'Tell us some information we need for your volunteer application'})))

    def __mentorFieldsets(self):
        self._fieldsets.extend((('Mentor Info', {'fields': ('description', 'origin', 'is_student', 'company',
                                                            'university', 'degree', 'first_timer', 'first_timer_extra',
                                                            'which_hack', 'quality', 'english_level', 'attendance',
                                                            'lennyface'),
                                                 'description': 'Tell us some information we need for your mentor '
                                                                'application'}),
                                ('Show us what you\'ve built',
                                 {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'),
                                  'description': 'Some of our sponsors may use this information for recruitment '
                                                 'purposes, '
                                                 'so please include as much as you can.'})
                                ))

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [('Personal Info',
                            {'fields': ('gender', 'other_gender', 'under_age', 'phone_number', 'tshirt_size', 'diet',
                                        'other_diet'),
                             'description': 'Hey there, before we begin we would like to know a little more about '
                                            'you.'})]
        if self.instance.is_hacker:
            self.__hackerFieldsets()
        elif self.instance.is_volunteer:
            self.__volunteerFieldsets()
        elif self.instance.is_mentor:
            self.__mentorFieldsets()
        elif self.instance.is_sponsor:
            self.__sponsorFieldsets()

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application

        help_texts = {
            'gender': 'This is for demographic purposes.',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited',
            'fav_movie': 'e.g.: Interstellar, Pirates of the Caribbean, Mulan, Twilight, etc.',
            'english_level': 'We just want to check which of you would be comfortable communicating in English!',
            'attendance': "It will be a great experience to enjoy from beginning to end with lots of things to do, "
                          "but it is ok if you can't make it the whole weekend!",
            'cool_skill': 'e.g: can lift 300kg deadweight, have web development skills, can read minds, '
                          'time traveler...',
            'friends': 'Remember that you all have to apply separately'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
            'friends': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'quality': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'weakness': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'cool_skill': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'which_hack': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'attendance': forms.RadioSelect(),
            'english_level': forms.RadioSelect(),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume (PDF)',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                getattr(settings, 'CURRENCY', '$'), settings.HACKATHON_NAME),
            'cool_skill': 'Do you have any cool skills we should know about?',
            'friends': 'If you are applying with some of your friends, please mention their names to know if we '
                       'should contact you in group',
            'quality': 'Tell us a quality of yourself',
            'weakness': 'Now tell us a weakness of yourself',
            'english_level': 'How much confident are you about talking in English?',
            'fav_movie': 'Which is your favorite movie?',
            'which_hack': 'Which ones?',
            'sponsor_position': 'What is your job position?',
            'company': 'On which company are you working?'
        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', 'type']
