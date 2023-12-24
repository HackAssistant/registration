from .base import *
#from .base import _HackerMentorApplication, _HackerMentorVolunteerApplication, _VolunteerMentorApplication, _VolunteerMentorSponsorApplication
class MentorApplication(
    BaseApplication,
 #   _HackerMentorApplication,
 #   _HackerMentorVolunteerApplication,
 #   _VolunteerMentorApplication,
 #   _VolunteerMentorSponsorApplication
):

    attendance = MultiSelectField(choices=ATTENDANCE)

    english_level = models.IntegerField(default=0, null=False, choices=ENGLISH_LEVEL)
    which_hack = MultiSelectField(choices=PREVIOUS_HACKS, null=True, blank=True)

    # Where is this person coming from?
    origin = models.CharField(max_length=300)

    # Is this your first hackathon?
    first_timer = models.BooleanField(default=False)

    # Random lenny face
    lennyface = models.CharField(max_length=300, default='-.-')

    # University
    graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
    university = models.CharField(max_length=300)
    degree = models.CharField(max_length=300)

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    # Hacker will assist face-to-face or online
    online = models.BooleanField(default=False)

    company = models.CharField(max_length=100, null=True, blank=True)
    why_mentor = models.CharField(max_length=500, null=False)
    first_time_mentor = models.BooleanField(null=False)
    fluent = models.CharField(max_length=150, null=False)
    experience = models.CharField(max_length=300, null=False)
    study_work = models.BooleanField(max_length=300, null=False)
    university = models.CharField(max_length=300, null=True, blank=True)
    degree = models.CharField(max_length=300, null=True, blank=True)
    participated = models.TextField(max_length=500, blank=True, null=True)
    resume = models.FileField(
        upload_to=resume_path_mentors,
        null=True,
        blank=True,
        validators=[validate_file_extension],
    )

    def can_be_edit(self, app_type="M"):
        return self.status in [APP_PENDING, APP_DUBIOUS] and not utils.is_app_closed(app_type)
