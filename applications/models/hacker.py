from .base import *
from .base import BaseApplication
#from .rest import _HackerMentorApplication, _HackerMentorVolunteerApplication

class HackerApplication(
    BaseApplication
   # _HackerMentorVolunteerApplication,
   # _HackerMentorApplication
):
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


    # Explain a little bit what projects have you done lately
    projects = models.TextField(max_length=500, blank=True, null=True)

    # META
    contacted = models.BooleanField(default=False)  # If a dubious application has been contacted yet
    contacted_by = models.ForeignKey(User, related_name='contacted_by', blank=True, null=True,
                                     on_delete=models.SET_NULL)

    reviewed = models.BooleanField(default=False)  # If a blacklisted application has been reviewed yet
    blacklisted_by = models.ForeignKey(User, related_name='blacklisted_by', blank=True, null=True,
                                       on_delete=models.SET_NULL)

    # Why do you want to come to X?
    description = models.TextField(max_length=500)

    # Reimbursement
    reimb = models.BooleanField(default=False)
    reimb_amount = models.FloatField(blank=True, null=True, validators=[
        MinValueValidator(0, "Negative? Really? Please put a positive value"),
        MaxValueValidator(150.0, "Not that much")])

    # Info for hardware
    hardware = models.CharField(max_length=300, null=True, blank=True)

    cvs_edition = models.BooleanField(default=False)

    resume = models.FileField(
        upload_to=resume_path_hackers,
        null=True,
        blank=True,
        validators=[validate_file_extension],
    )

    @classmethod
    def annotate_vote(cls, qs):
        return qs.annotate(vote_avg=Avg('vote__calculated_vote'))

    def invalidate(self):
        if self.status != APP_DUBIOUS:
            raise ValidationError('Applications can only be marked as invalid if they are dubious first')
        self.status = APP_INVALID
        self.save()

    def set_dubious(self):
        self.status = APP_DUBIOUS
        self.contacted = False
        self.status_update_date = timezone.now()
        self.vote_set.all().delete()
        if hasattr(self, 'acceptedresume'):
            self.acceptedresume.delete()
        self.save()

    def unset_dubious(self):
        self.status = APP_PENDING
        self.status_update_date = timezone.now()
        self.save()

    def set_contacted(self, user):
        if not self.contacted:
            self.contacted = True
            self.contacted_by = user
            self.save()

    def confirm_blacklist(self, user, motive_of_ban):
        if self.status != APP_BLACKLISTED:
            raise ValidationError('Applications can only be confirmed as blacklisted if they are blacklisted first')
        self.status = APP_INVALID
        self.set_blacklisted_by(user)
        blacklist_user = BlacklistUser.objects.filter(email=self.user.email).first()
        if not blacklist_user:
            blacklist_user = BlacklistUser.objects.create_blacklist_user(
                self.user, motive_of_ban)
        blacklist_user.save()
        self.save()

    def set_blacklist(self):
        self.status = APP_BLACKLISTED
        self.status_update_date = timezone.now()
        self.save()

    def unset_blacklist(self):
        self.status = APP_PENDING
        self.status_update_date = timezone.now()
        self.save()

    def set_blacklisted_by(self, user):
        if not self.blacklisted_by:
            self.blacklisted_by = user

    def is_blacklisted(self):
        return self.status == APP_BLACKLISTED

    def can_be_edit(self, app_type="H"):
        return self.status in [APP_PENDING, APP_DUBIOUS, APP_INVITED] and not self.vote_set.exists() and not \
            utils.is_app_closed(app_type)



class AcceptedResume(models.Model):
    application = models.OneToOneField(HackerApplication, primary_key=True, on_delete=models.CASCADE)
    accepted = models.BooleanField()
