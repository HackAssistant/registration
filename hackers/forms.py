from django import forms
from django.conf import settings
from form_utils.forms import BetterModelForm

from hackers import models


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
        label='How old will you be by %s?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'I\'ll be 18 or over by then'), (True, 'I\'ll be under age')),
        widget=forms.RadioSelect
    )

    team = forms.TypedChoiceField(
        required=True,
        label='Are you applying as a team?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

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
                         ' http://textsmili.es/</a>'
        }

        fieldsets = (
            ('Personal Info',
             {'fields': ('gender', 'university', 'degree',
                         'graduation_year', 'tshirt_size', 'diet', 'other_diet', 'under_age', 'lennyface'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Show us what you\'ve built', {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'), }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects'), }),
            ('Where are you joing us from?', {'fields': ('origin_city', 'origin_country', 'scholarship',), }),
            ('Team', {'fields': ('team', 'teammates',), }),
        )

        widgets = {
            'origin_country': forms.TextInput(attrs={'autocomplete': 'off'}),
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
            'description': 'What are you most excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on? '
                        'You can talk about about past hackathons, personal projects, awards etc. (we love links) '
                        'Show us your passion! :D',
            'resume': 'Upload your resume',
            'teammates': 'What are your teammates\'s full names?'

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status',
                   'authorized_privacy', ]
