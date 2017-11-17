from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from form_utils.forms import BetterModelForm

from applications import models


class ApplicationForm(BetterModelForm):
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
    university = forms.CharField(required=True,
                                 label='What university are you studying in?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your Major?',
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

    scholarship = forms.TypedChoiceField(
        required=True,
        label='Do you need travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
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

    team = forms.TypedChoiceField(
        required=True,
        label='Are you applying as a team?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    code_conduct = forms.BooleanField(required=False,
                                      label='I have read and accept '
                                            '<a href="/code_conduct" target="_blank">%s Code of conduct</a>' % (
                                                settings.HACKATHON_NAME), )

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        if resume._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep filesize under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(resume._size)))
        return resume

    def clean_code_conduct(self):
        cc = self.cleaned_data.get('code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError("In order to apply and attend you have to accept our code of conduct")
        return cc

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('gender', 'university', 'degree',
                         'graduation_year', 'tshirt_size', 'diet', 'other_diet', 'under_age', 'lennyface'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Show us what you\'ve built', {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'), }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects'), }),
            ('Where are you joining us from?', {'fields': ('origin_city', 'origin_country', 'scholarship',), }),
            ('Team', {'fields': ('team', 'teammates',), }),
        ]
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(('Code of Conduct', {'fields': ('code_conduct',)}))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this '
                      'question if you want',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major?',
            'teammatess': 'Add each teammate in a new line.',
            'diet': 'If you select Others, please write detail in the "Other diet" field that will appear',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D'
        }

        widgets = {
            'origin_country': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'tshirt_size': forms.RadioSelect(),
            'graduation_year': forms.RadioSelect(),
        }

        labels = {
            'gender': 'What gender do you associate with?',
            'graduation_year': 'What year are you graduating?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin_city': 'City',
            'origin_country': 'Country',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'teammates': 'What are your teammates\'s full names?'

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status',
                   'authorized_privacy', ]
