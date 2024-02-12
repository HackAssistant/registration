from .base import *
from .base import _BaseApplicationForm


class HackerApplicationForm(_BaseApplicationForm):
    bootstrap_field_info = {
        "Personal Info": {
            "fields": [
                {"name": "university", "space": 12},
                {"name": "degree", "space": 12},
                {"name": "graduation_year", "space": 12},
                {"name": "gender", "space": 12},
                {"name": "other_gender", "space": 12},
                {"name": "phone_number", "space": 12},
                {"name": "tshirt_size", "space": 12},
                {"name": "under_age", "space": 12},
                {"name": "lennyface", "space": 12},
            ],
            "description": "Hey there, before we begin we would like to know a little more about you.",
        },
        "Hackathons": {
            "fields": [
                {"name": "description", "space": 12},
                {"name": "first_timer", "space": 12},
                {"name": "projects", "space": 12},
            ]
        },
        "Show us what you've built": {
            "fields": [
                {"name": "github", "space": 12},
                {"name": "devpost", "space": 12},
                {"name": "linkedin", "space": 12},
                {"name": "site", "space": 12},
                {"name": "resume", "space": 12},
            ],
            "description": "Some of our sponsors may use this information for recruitment purposes,"
            "so please include as much as you can.",
        },
    }

    github = social_media_field("github", "https://github.com/biene")
    devpost = social_media_field("devpost", "https://devpost.com/biene")
    linkedin = social_media_field("linkedin", "https://www.linkedin.com/in/biene")
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

    # def clean_site(self,):
    #     data = self.cleaned_data["site"]

    #     if not URLValidator(data):
    #         raise forms.ValidationError("Please enter a valid website url")
    #     return data

    first_timer = common_first_timer()

    university = common_university()

    degree = forms.CharField(
        required=True,
        label="What's your major/degree?",
        help_text="Current or most recent degree you've received",
        widget=forms.TextInput(
            attrs={"class": "typeahead-degrees", "autocomplete": "off"}
        ),
    )

    cvs_edition = forms.BooleanField(
        required=False,
        label='I authorize "Hackers at UPC" to share my CV with HackUPC 2024 Sponsors.',
    )

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
    ):
        super().__init__(
            data,
            files,
            auto_id,
            prefix,
            initial,
            error_class,
            label_suffix,
            empty_permitted,
            instance,
            use_required_attribute,
        )
        self.fields["resume"].required = True

    def clean_cvs_edition(self):
        cc = self.cleaned_data.get("cvs_edition", False)
        return cc

    def clean_reimb_amount(self):
        data = self.cleaned_data["reimb_amount"]
        reimb = self.cleaned_data.get("reimb", False)
        if reimb and not data:
            raise forms.ValidationError(
                "To apply for reimbursement please set a valid amount."
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
        # Fieldsets ordered and with description
        discord = getattr(settings, "DISCORD_HACKATHON", False)
        hybrid = getattr(settings, "HYBRID_HACKATHON", False)
        personal_info_fields = fields["Personal Info"]["fields"]
        personal_info_fields.append({"name": "online", "space": 12})
        if not hybrid:
            self.fields["online"].widget = forms.HiddenInput()
        polices_fields = [
            {"name": "cvs_edition", "space": 12},
            {"name": "email_subscribe", "space": 12},
            {"name": "terms_and_conditions", "space": 12},
        ]
        if not discord:
            personal_info_fields.extend(
                [
                    {"name": "diet", "space": 12},
                    {"name": "other_diet", "space": 12},
                ]
            )
            polices_fields.append({"name": "diet_notice", "space": 12})

        personal_info_fields.append({"name": "discover", "space": 12})
        deadline = getattr(settings, "REIMBURSEMENT_DEADLINE", False)
        r_enabled = getattr(settings, "REIMBURSEMENT_ENABLED", False)
        personal_info_fields.append({"name": "origin", "space": 12})

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
        model = models.HackerApplication
        extensions = getattr(settings, "SUPPORTED_RESUME_EXTENSIONS", None)

        help_texts = {
            "gender": "This is for demographic purposes. You can skip this question if you want.",
            "degree": "What's your major/degree?",
            "other_diet": "Please fill here in your dietary requirements. We want to make sure we have food for you!",
            "lennyface": 'tip: you can chose from here <a href="http://textsmili.es/" target="_blank">'
            " http://textsmili.es/</a>",
            "projects": "You can talk about about past hackathons, personal projects, awards etc. "
            "(we love links) Show us your passion! :D",
            "reimb_amount": "We try our best to cover costs for all hackers, but our budget is limited",
            "resume": "Accepted file formats: %s"
            % (", ".join(extensions) if extensions else "Any"),
            "origin": "If you don’t see your city, choose the closest one! "
            "Please type following this schema: <strong>city, province, country</strong>",
        }

        class CustomSelect(forms.Select):
            def create_option(
                self, name, value, label, selected, index, subindex=None, attrs=None
            ):
                if index == 0:
                    attrs = {"disabled": "disabled"}
                return super().create_option(
                    name, value, label, selected, index, subindex=subindex, attrs=attrs
                )

        def clean_discover(self):
            discover = self.cleaned_data.get("discover")
            if discover == "":
                raise forms.ValidationError("Please select an option.")
            return discover

        discover_choices = (
            ("", "- Select an option -"),
            (1, "HackUPC's social media"),
            (2, "Through your university (social media, emails...)"),
            (3, "Friends"),
            (4, "Posters"),
            (5, "Other hackathons"),
            (6, "Online ads"),
            (7, "Past editions"),
            (8, "Other"),
        )

        widgets = {
            "origin": forms.TextInput(attrs={"autocomplete": "off"}),
            "description": forms.Textarea(attrs={"rows": 3, "cols": 40}),
            "projects": forms.Textarea(attrs={"rows": 3, "cols": 40}),
            "discover": CustomSelect(choices=discover_choices),
            "graduation_year": forms.RadioSelect(),
        }

        labels = {
            "gender": "What gender do you identify as?",
            "other_gender": "Self-describe",
            "graduation_year": "What year are you expecting to graduate?",
            "tshirt_size": "What's your t-shirt size?",
            "diet": "Dietary requirements",
            "phone_number": "Phone number (Optional)",
            "lennyface": 'Which "lenny face" represents you better?',
            "discover": "How did you hear about us?",
            "origin": "Where are you joining us from?",
            "description": "Why are you excited about %s?" % settings.HACKATHON_NAME,
            "projects": "What projects have you worked on?",
            "resume": "Upload your resume",
        }
