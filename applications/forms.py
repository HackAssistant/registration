from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from app.utils import validate_url
from applications import models


def set_field_html_name(cls, new_name):
    """
    This creates wrapper around the normal widget rendering,
    allowing for a custom field name (new_name).
    """
    old_render = cls.widget.render

    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    cls.widget.render = _widget_render_wrapper


class _BaseApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+#########'}))
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

    def clean_code_conduct(self):
        cc = self.cleaned_data.get('code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "To attend %s you must abide by our code of conduct" % settings.HACKATHON_NAME)
        return cc

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
        item = super(_BaseApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    class Meta:
        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', ]


class _HackerMentorVolunteerApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
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


class _HackerMentorApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
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
            raise forms.ValidationError("Please fill this in order for us to know you a bit better")
        return data


class HackerApplicationForm(_BaseApplicationForm, _HackerMentorApplicationForm, _HackerMentorVolunteerApplicationForm):
    reimb = forms.TypedChoiceField(
        required=False,
        label='Do you need a travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

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

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('university', 'degree', 'graduation_year', 'gender', 'other_gender',
                         'phone_number', 'tshirt_size', 'diet', 'other_diet',
                         'under_age', 'lennyface'),
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
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(HackerApplicationForm, self).fieldsets

    class Meta(_BaseApplicationForm.Meta):
        model = models.HackerApplication
        extensions = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

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
            'resume': 'Accepted file formats: %s' % (', '.join(extensions) if extensions else 'Any')
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
        label='Have you volunteered at %s before?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )
    which_hack = forms.MultipleChoiceField(
        required=False,
        label='Which %s editions have you volunteered in?' % settings.HACKATHON_NAME,
        widget=forms.CheckboxSelectMultiple,
        choices=models.PREVIOUS_HACKS
    )

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

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('origin', 'university', 'degree', 'graduation_year', 'gender', 'other_gender',
                         'phone_number', 'tshirt_size', 'diet', 'other_diet',
                         'under_age', 'lennyface'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Volunteer Skills', {'fields': ('first_timer', 'first_time_volunteer', 'which_hack', 'attendance',
                                             'english_level', 'quality', 'weakness', 'cool_skill', 'fav_movie',
                                             'friends')}),
        ]
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(VolunteerApplicationForm, self).fieldsets

    class Meta(_BaseApplicationForm.Meta):
        model = models.VolunteerApplication
        help_texts = {
            'gender': 'This is for demographic purposes.',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'attendance': "It will be a great experience to enjoy from beginning to end with lots of things to do, "
                          "but it is ok if you can't make it the whole weekend!",
            'english_level': "No English level needed to volunteer, we just want to check which of you would be"
                             " comfortable doing tasks that require communication in English!",
            'fav_movie': 'e.g.: Interstellar, Pirates of the Caribbean, Mulan, Twilight, etc.',
            'cool_skill': 'e.g: can lift 300kg deadweight, have web development skills, can read minds, '
                          'time traveler...',
            'friends': '*Remember that you all have to apply separately'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'graduation_year': forms.RadioSelect(),
            'english_level': forms.RadioSelect(),
            'friends': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'weakness': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'quality': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'graduation_year': 'What year will you graduate?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin': 'Where are you joining us from?',
            'which_hack': 'Which %s editions have you volunteered in?' % settings.HACKATHON_NAME,
            'attendance': 'Will you be attending HackUPC for the whole event?',
            'english_level': 'How much confident are you about talking in English?',
            'quality': 'Tell us a quality of yourself :)',
            'weakness': 'Now a weakness :(',
            'cool_skill': 'Do you have any cool skills we should know about?',
            'fav_movie': 'Which is your favorite movie?',
            'friends': 'If you are applying with some of your friends, please mention their names'
        }


class MentorApplicationForm(_BaseApplicationForm, _HackerMentorApplicationForm, _HackerMentorVolunteerApplicationForm):
    first_time_mentor = forms.TypedChoiceField(
        required=True,
        label='Have you mentored at %s before?' % settings.HACKATHON_NAME,
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
                              help_text='Current or most recent company you attended.',
                              label='Where are you working at?')

    university = forms.CharField(required=False,
                                 label='What university do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=False, label='What\'s your major/degree?',
                             help_text='Current or most recent degree you\'ve received',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    def mentor(self):
        return True

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('origin', 'study_work', 'company', 'university', 'degree', 'graduation_year', 'gender',
                         'other_gender', 'phone_number', 'tshirt_size', 'diet', 'other_diet', 'under_age',
                         'lennyface'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Mentor Skills', {'fields': ('why_mentor', 'first_timer', 'first_time_mentor', 'which_hack',
                                          'participated', 'attendance', 'english_level', 'fluent', 'experience')}),
            ('Show us what you\'ve built',
             {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume',)}),
        ]
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(MentorApplicationForm, self).fieldsets

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
            if not self.cleaned_data['company']:
                self.add_error('company', 'Type your company, please')

        return super(MentorApplicationForm, self).clean()

    class Meta(_BaseApplicationForm.Meta):
        model = models.MentorApplication
        extensions = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

        help_texts = {
            'gender': 'This is for demographic purposes.',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'participated': 'You can talk about about past hackathons or any other events. ',
            'resume': 'Accepted file formats: %s' % (', '.join(extensions) if extensions else 'Any'),
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'participated': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
            'english_level': forms.RadioSelect(),
            'fluent': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'experience': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'why_mentor': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
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
            'participated': 'Have you participated in other hackathons or tech events?',
            'resume': 'Upload your resume',
            'why_mentor': 'Why do you want to participate as mentor?',
            'which_hack': 'Which editions have you mentored?',
            'attendance': 'Will you be attending HackUPC for the whole event?',
            'english_level': 'How much confident are you about talking in English?',
            'fluent': 'What program languages are you fluent on?',
            'experience': 'Which program languages have you experience on?'
        }


class SponsorForm(_BaseApplicationForm):

    def fieldsets(self):
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('gender', 'other_gender', 'under_age', 'phone_number', 'tshirt_size', 'diet', 'other_diet'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Sponsor Info',
             {'fields': ('company', 'position', 'attendance')})
        ]
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(SponsorForm, self).fieldsets

    def save(self, commit=True):
        application = super(SponsorForm, self).save(commit=False)
        application.confirm()
        if commit:
            application.save()
        return application

    class Meta(_BaseApplicationForm.Meta):
        model = models.SponsorApplication
        help_texts = {
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'gender': 'This is for demographic purposes.',
        }
        labels = {
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'attendance': 'What availability will you have during the event?',
            'company': 'On behalf of which company are you coming?',
            'position': 'What is your job position?',
        }
