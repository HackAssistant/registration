from .base import *
class SponsorForm(OverwriteOnlyModelFormMixin, BootstrapFormMixin, ModelForm):
    diet = forms.ChoiceField(required=True, choices=models.DIETS)
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
                       {'name': 'tshirt_size', 'space': 12}, {'name': 'position', 'space': 12},
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
