from .base import *
from .base import _BaseApplicationForm


class VolunteerApplicationForm(_BaseApplicationForm):
    first_timer = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )
    first_time_volunteer = forms.TypedChoiceField(
        required=True,
        label="Is it your first time volunteering in %s?" % settings.HACKATHON_NAME,
        coerce=lambda x: x == "True",
        choices=((True, "Yes"), (False, "No")),
        widget=forms.RadioSelect,
    )
    which_hack = forms.MultipleChoiceField(
        required=False,
        label="Which %s editions have you volunteered in?" % settings.HACKATHON_NAME,
        widget=forms.CheckboxSelectMultiple,
        choices=models.PREVIOUS_HACKS,
    )
    under_age = forms.TypedChoiceField(
        required=True,
        label="Are you over the age of 18 years old?",
        initial=False,
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
    )
    night_shifts = forms.TypedChoiceField(
        required=False,
        label="Would you be okay with doing night shifts?",
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Yes"), (None, "Maybe")),
        widget=forms.RadioSelect,
    )
    lennyface = forms.TypedChoiceField(
        required=True,
        label="Will you be in Barcelona from April to May?",
        coerce=lambda x: x == "True",
        choices=((False, "Doubtful"), (True, "Yes")),
        help_text="The event is in May, however, we kindly request your presence at the preceding meetings in person!",
        widget=forms.RadioSelect,
    )
    university = forms.CharField(
        initial="NA", widget=forms.HiddenInput(), required=False
    )
    degree = forms.CharField(initial="NA", widget=forms.HiddenInput(), required=False)

    bootstrap_field_info = {
        "Personal Info": {
            "fields": [
                {"name": "pronouns", "space": 12},
                {"name": "gender", "space": 12},
                {"name": "under_age", "space": 12},
                {"name": "lennyface", "space": 12},
                {"name": "other_gender", "space": 12},
                {"name": "origin", "space": 12},
            ],
            "description": "Hey there, we need some information before we start :)",
        },
        "Volunteering": {
            "fields": [
                {"name": "first_time_volunteer", "space": 12},
                {"name": "which_hack", "space": 12},
                {"name": "english_level", "space": 12},
                {"name": "attendance", "space": 12},
                {"name": "volunteer_motivation", "space": 12},
            ],
        },
        "Some other questions": {
            "fields": [
                {"name": "friends", "space": 12},
                {"name": "night_shifts", "space": 12},
                {"name": "tshirt_size", "space": 12},
            ],
            "description": "Don’t panic! There are just a few more questions ",'
        },
        "Personal Interests": {
            "fields": [
                {"name": "fav_movie", "space": 12},
                {"name": "quality", "space": 12},
                {"name": "weakness", "space": 12},
                {"name": "hobbies", "space": 12},
                {"name": "cool_skill", "space": 12},
                # Hidden
                {"name": "graduation_year", "space": 12},
                {"name": "university", "space": 12},
                {"name": "degree", "space": 12},
            ],
            "description": "We want to get to know you!",
        },
    }

    def clean(self):
        data = self.cleaned_data["which_hack"]
        volunteer = self.cleaned_data["first_time_volunteer"]
        if not volunteer and not data:
            self.add_error("which_hack", "Choose the hackathons you volunteered")

        return super(VolunteerApplicationForm, self).clean()

    def volunteer(self):
        return True

    def clean_reimb_amount(self):
        data = self.cleaned_data["reimb_amount"]
        reimb = self.cleaned_data.get("reimb", False)
        if reimb and not data:
            raise forms.ValidationError(
                "To apply for reimbursement please set a valid amount"
            )
        deadline = getattr(settings, "REIMBURSEMENT_DEADLINE", False)
        if data and deadline and deadline <= timezone.now():
            raise forms.ValidationError(
                "Reimbursement applications are now closed. Trying to hack us?"
            )
        return data

    def clean_reimb(self):
        reimb = self.cleaned_data.get("reimb", False)
        deadline = getattr(settings, "REIMBURSEMENT_DEADLINE", False)
        if reimb and deadline and deadline <= timezone.now():
            raise forms.ValidationError(
                "Reimbursement applications are now closed. Trying to hack us?"
            )
        return reimb

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, "DISCORD_HACKATHON", False)
        other_fields = fields["Some other questions"]["fields"]
        polices_fields = [
            {"name": "terms_and_conditions", "space": 12},
            {"name": "email_subscribe", "space": 12},
        ]
        if not discord:
            other_fields.extend(
                [
                    {"name": "diet", "space": 12},
                    {"name": "other_diet", "space": 12},
                ]
            )
            polices_fields.append({"name": "diet_notice", "space": 12})
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            fields["HackUPC Policies"] = {
                "fields": polices_fields,
                "description": '<p style="color: margin-top: 1em;display: block;'
                'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                "process your information to organize an awesome hackathon. It "
                "will also include images and videos of yourself during the event. "
                "Your data will be used for admissions mainly. We may also reach "
                "out to you (sending you an e-mail) about other events that we are "
                "organizing and that are of a similar nature to those previously "
                "requested by you. For more information on the processing of your "
                "personal data and on how to exercise your rights of access, "
                "rectification, suppression, limitation, portability and opposition "
                "please visit our Privacy and Cookies Policy.</p>",
            }
        return fields

    class Meta(_BaseApplicationForm.Meta):
        model = models.VolunteerApplication
        help_texts = {
            "degree": "What's your major/degree?",
            "other_diet": "Please fill here in your dietary requirements. We want to make sure we have food for you!",
            "attendance": "It will be a great experience to enjoy from beginning to end with lots of things to do, "
            "but it is ok if you can't make it the whole weekend!",
            "english_level": "No English level needed to volunteer, we just want to check which of you would be"
            " comfortable doing tasks that require communication in English!",
            "fav_movie": "e.g.: Interstellar, Game of Thrones,  Avatar, La Casa de Papel, etc.",
            "cool_skill": "The 3 most original will have a small prize to be given at the 2nd volunteer meeting ",
            "friends": "Remember that you all have to apply separately",
            "origin": "This is for demographic purposes",
            "volunteer_motivation": "It can be a short answer, we are just curious 😛",'
        }

        widgets = {
            "origin": forms.TextInput(attrs={"autocomplete": "off"}),
            "english_level": forms.RadioSelect(),
            "friends": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "weakness": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "quality": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "hobbies": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "pronouns": forms.TextInput(
                attrs={"autocomplete": "off", "placeholder": "their/them"}
            ),
            "graduation_year": forms.HiddenInput(),
            "phone_number": forms.HiddenInput(),
            "lennyface": forms.RadioSelect(),
        }

        labels = {
            "pronouns": "Enter your pronouns",
            "gender": "What gender do you identify as?",
            "other_gender": "Self-describe",
            "graduation_year": "What year will you graduate?",
            "tshirt_size": "What's your t-shirt size?",
            "diet": "Do you have any dietary restrictions? ",
            "origin": "Where are you joining us from?",
            "which_hack": "Which %s editions have you volunteered in?"
            % settings.HACKATHON_NAME,
            "attendance": "Which days will you attend to HackUPC?",
            "english_level": "What is your English level?",
            "quality": "Name a quality of yours:",
            "weakness": "Now a weakness:",
            "cool_skill": "What is a cool skill or fun fact about you? Surprise us 🎉",
            "fav_movie": "What is your favorite movie or series?",
            "friends": "Are you applying with some friends? Enter their complete names",
            "hobbies": "What are your hobbies or what do you do for fun?",
            "volunteer_motivation": "Why do you want to volunteer at HackUPC?",
        }
