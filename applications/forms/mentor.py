from .base import *
from .base import _BaseApplicationForm


class MentorApplicationForm(_BaseApplicationForm):
    first_timer = common_first_timer()
    university = common_university()
    degree = common_degree()
    #Mandatory social fields
    linkedin = social_required("linkedin", "https://www.linkedin.com/in/john_biene")

    # Socials
    github = social_media_field("github", "https://github.com/johnBiene")
    devpost = social_media_field("devpost", "https://devpost.com/JohnBiene")
    site = social_media_field("site", "https://biene.space")

    online = common_online()

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        size = getattr(resume, "_size", 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(
                "Please keep resume size under %s. Current filesize %s"
                % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size))
            )
        return resume

    def clean_github(self):
        data = self.cleaned_data["github"]
        validate_url(data, "github.com")
        return data

    def clean_devpost(self):
        data = self.cleaned_data["devpost"]
        validate_url(data, "devpost.com")
        return data

    def clean_linkedin(self):
        data = self.cleaned_data["linkedin"]
        validate_url(data, "linkedin.com")
        return data


    def clean_projects(self):
        data = self.cleaned_data["projects"]
        first_timer = self.cleaned_data["first_timer"]
        if not first_timer and not data:
            raise forms.ValidationError(
                "Please fill this in order for us to know you a bit better."
            )
        return data

    first_time_mentor = forms.TypedChoiceField(
        required=True,
        label="Have you participated as mentor in past HackUPC editions?",
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Yes")),
        widget=forms.RadioSelect,
    )

    study_work = forms.TypedChoiceField(
        required=True,
        label="Are you studying or working?",
        coerce=lambda x: x == "True",
        choices=((False, "Working"), (True, "Studying")),
        widget=forms.RadioSelect,
    )

    company = forms.CharField(
        required=False,
        help_text="Backend developer, DevOps…",
        label="What is your current role?",
    )

    university = forms.CharField(
        initial="NA", widget=forms.HiddenInput(), required=False
    )

    degree = forms.CharField(
        required=False,
        label="What's your major/degree of study?",
        help_text="Current or most recent degree you've received",
        widget=forms.TextInput(
            attrs={"class": "typeahead-degrees", "autocomplete": "off"}
        ),
    )

    graduation_year = forms.ChoiceField(
        required=False,
        choices=models.YEARS,
        help_text="What year have you graduated on or when will you graduate",
        label="What year will you graduate?",
        widget=forms.RadioSelect(),
    )

    bootstrap_field_info = {
        "Personal Information": {
            "fields": [
                {"name": "origin", "space": 12},
                {"name": "gender", "space": 12},
                {"name": "other_gender", "space": 12},
                {"name": "tshirt_size", "space": 12},
                {"name": "under_age", "space": 12},
                {"name": "lennyface", "space": 12},
            ],
            "description": "Hey there, before we begin we would like to know a little more about you.",
        },
        "Background information": {
            "fields": [
                {"name": "study_work", "space": 12},
                {"name": "company", "space": 12},
                {"name": "university", "space": 12},
                {"name": "degree", "space": 12},
                {"name": "graduation_year", "space": 12},
                {"name": "english_level", "space": 12},
                {"name": "fluent", "space": 12},
                {"name": "experience", "space": 12},
                {"name": "linkedin", "space": 12},
                {"name": "site", "space": 12},
                {"name": "github", "space": 12},
                {"name": "devpost", "space": 12},
                {"name": "resume", "space": 12},
            ],
        },
        "Hackathons": {
            "fields": [
                {"name": "why_mentor", "space": 12},
                {"name": "first_timer", "space": 12},
                {"name": "first_time_mentor", "space": 12},
                {"name": "which_hack", "space": 12},
                {"name": "participated", "space": 12},
                {"name": "attendance", "space": 12},
            ],
        },
    }

    def mentor(self):
        return True

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, "DISCORD_HACKATHON", False)
        hybrid = getattr(settings, "HYBRID_HACKATHON", False)
        personal_info_fields = fields["Personal Information"]["fields"]
        polices_fields = [
            {"name": "terms_and_conditions", "space": 12},
            {"name": "email_subscribe", "space": 12},
        ]
        personal_info_fields.append({"name": "online", "space": 12})
        if not hybrid:
            self.fields["online"].widget = forms.HiddenInput()
        if not discord:
            personal_info_fields.extend(
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

    def clean(self):
        data = self.cleaned_data["which_hack"]
        mentor = self.cleaned_data["first_time_mentor"]
        if mentor and not data:
            self.add_error("which_hack", "Choose the hackathons you mentored")
        study = self.cleaned_data["study_work"]
        if study:
            if not self.cleaned_data["university"]:
                self.add_error("university", "Type your university, please")
            if not self.cleaned_data["degree"]:
                self.add_error("degree", "Type your degree, please")
            if not self.cleaned_data["graduation_year"]:
                self.add_error("graduation_year", "Choose your graduation year, please")
        else:
            self.cleaned_data["graduation_year"] = models.DEFAULT_YEAR
            if not self.cleaned_data["company"]:
                self.add_error("company", "Type your company, please")

        return super(MentorApplicationForm, self).clean()

    class Meta(_BaseApplicationForm.Meta):
        model = models.MentorApplication
        extensions = getattr(settings, "SUPPORTED_RESUME_EXTENSIONS", None)

        help_texts = {
            "gender": "This is for demographic purposes.",
            # 'degree': 'What\'s your major/degree?',
            "other_diet": "Please fill here in your dietary requirements. We want to make sure we have food for you!",
            "lennyface": 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
            " http://textsmili.es/</a>",
            "participated": "You can talk about about past hackathons or any other events. ",
            "resume": "Accepted file formats: %s"
            % (", ".join(extensions) if extensions else "Any"),
            "fluent": "Catalan, French, Chinese, Arabic…",
            "experience": "C++, Java, Docker, Vue, AWS…",
        }

        widgets = {
            "origin": forms.TextInput(attrs={"autocomplete": "off"}),
            "participated": forms.Textarea(attrs={"rows": 3, "cols": 40}),
            "graduation_year": forms.RadioSelect(),
            "english_level": forms.RadioSelect(),
            "fluent": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "experience": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "why_mentor": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "first_timer": forms.HiddenInput(),
            "lennyface": forms.HiddenInput(),
            "resume": forms.FileInput(),
        }

        labels = {
            "gender": "What gender do you identify as?",
            "other_gender": "Self-describe",
            "graduation_year": "What year will you graduate?",
            "tshirt_size": "What is your t-shirt size?",
            "diet": "Dietary requirements",
            "lennyface": 'Describe yourself in one "lenny face"?',
            "origin": "Where are you joining us from?",
            "description": "Why are you excited about %s?" % settings.HACKATHON_NAME,
            "participated": "Have you participated as mentor in other hackathons or tech events?",
            "resume": "Upload your resume",
            "why_mentor": "Why do you want to participate as mentor?",
            "which_hack": "Which editions have you mentored?",
            "attendance": "Which days will you be attending HackUPC?",
            "english_level": "How confident are you speaking in English?",
            "fluent": "What languages do you speak?",
            "experience": "What technologies/programming languages do you know?",
        }
