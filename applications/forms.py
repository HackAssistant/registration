from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm

from app.utils import validate_url
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
    phone_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+#########'}))
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

    reimb = forms.TypedChoiceField(
        required=False,
        label='Do you need travel reimbursement to attend?',
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
                                      label='I have read and accept '
                                            '<a href="/code_conduct" target="_blank">%s Code of conduct</a>' % (
                                                settings.HACKATHON_NAME), )

    mlh_code_conduct = forms.BooleanField(required=False,
                                          label='I will at all times abide by and conform to the Major League Hacking '
                                                '<a href="https://mlh.io/code-of-conduct">Code of Conduct</a> while at'
                                                ' the event.')
    mlh_data_sharing = forms.BooleanField(required=False,
                                          label='I agree to the terms of both the '
                                                '<a href="http://bit.ly/mlh_t_c">MLH Contest Terms and Conditions</a>'
                                                ' and the <a href="https://mlh.io/privacy">MLH Privacy Policy</a>. '
                                                'Please note that you may receive pre and post-event informational '
                                                'e-mails and occasional messages about hackathons from MLH as per the '
                                                'MLH Privacy Policy.')

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
            raise forms.ValidationError("In order to apply and attend you have to accept our code of conduct")
        return cc

    def clean_mlh_code_conduct(self):
        cc = self.cleaned_data.get('mlh_code_conduct', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError("In order to apply and attend you have to accept MLH Code of Conduct")
        return cc

    def clean_mlh_data_sharing(self):
        cc = self.cleaned_data.get('mlh_data_sharing', False)
        # Check that if it's the first submission hackers checks code of conduct checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError("In order to apply and attend you have to accept MLH data sharing policy")
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
        return data

    def clean_other_diet(self):
        data = self.cleaned_data['other_diet']
        diet = self.cleaned_data['diet']
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please fill your specific diet requirements")
        return data

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('gender', 'university', 'degree', 'phone_number',
                         'graduation_year', 'tshirt_size', 'diet', 'other_diet',
                         'under_age', 'lennyface'),
              'description': 'Hey there, before we begin we would like to know a little more about you.', }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'projects'), }),
            ('Show us what you\'ve built', {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'), }),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Traveling', {'fields': ('origin',)}))
        else:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'reimb', 'reimb_amount'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            self._fieldsets.append(
                ('Code of Conduct', {'fields': ('code_conduct', 'mlh_data_sharing', 'mlh_code_conduct')}))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'gender': 'This is for demographic purposes. You can skip this '
                      'question if you want',
            'graduation_year': 'What year have you graduated on or when will '
                               'you graduate',
            'degree': 'What\'s your major?',
            'other_diet': 'Please fill here your dietary restrictions. We want to make sure we have food for you!',
            'lennyface': 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
                         ' http://textsmili.es/</a>',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
            'reimb_amount': 'We try our best to cover costs for all hackers, but our budget is limited'
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
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
            'origin': 'Where are you joining us from?',
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on?',
            'resume': 'Upload your resume',
            'reimb_amount': 'How much money (%s) would you need to afford traveling to %s?' % (
                settings.CURRENCY, settings.HACKATHON_NAME),

        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', ]
