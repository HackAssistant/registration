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
    university = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    first_timer = forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'Yes'), (True, 'No')),
        widget=forms.RadioSelect
    )

    scholarship = forms.TypedChoiceField(
        required=True,
        label='Do you need travel reimbursement to attend?',
        coerce=lambda x: x == 'True',
        choices=((False, 'Yes'), (True, 'No')),
        widget=forms.RadioSelect
    )

    under_age = forms.TypedChoiceField(
        required=True,
        label='Will you be under 18 by %s?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'Yes'), (True, 'No')),
        widget=forms.RadioSelect
    )

    class Meta:
        model = models.Application

        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this '
                      'question if you want',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major?',
            'diet': 'If you select Others, please write detail in the "Other diet" field that will appear',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>'
        }

        fieldsets = (
            ('Personal Info',
             {'fields': ('gender', 'university', 'degree',
                         'graduation_year', 'tshirt_size', 'diet', 'other_diet', 'under_age'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Show us what you\'ve built', {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'), }),
            ('Hackathons?', {'fields': ('description', 'projects', 'first_timer',), }),
            ('Where are you joing us from?', {'fields': ('origin_city', 'origin_country', 'scholarship',), }),
        )

        labels = {
            'gender': 'What gender do you associate with?',
            'lennyface': 'Describe yourself in one "lenny face"?',
            'origin_city': 'What city are you coming from?',
            'origin_country': 'What country are you coming from?',
            'description': 'What are you most excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on? '
                        'You can talk about about past hackathons, personal projects, awards etc. (we love links) '
                        'Show us your passion! :D',
            'resume': 'Upload your resume'

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status',
                   'authorized_privacy']
