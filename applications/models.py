from __future__ import unicode_literals

import uuid as uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from datetime import date, timedelta

from app import utils
from user.models import User

import random, string

NO_ANSWER = 'NA'
OTHER = 'O'

APP_PENDING = 'P'
APP_REJECTED = 'R'
APP_INVITED = 'I'
APP_LAST_REMIDER = 'LR'
APP_CONFIRMED = 'C'
APP_CANCELLED = 'X'
APP_ATTENDED = 'A'
APP_EXPIRED = 'E'

STATUS = [
    (APP_PENDING, 'Under review'),
    (APP_REJECTED, 'Wait listed'),
    (APP_INVITED, 'Invited'),
    (APP_LAST_REMIDER, 'Last reminder'),
    (APP_CONFIRMED, 'Confirmed'),
    (APP_CANCELLED, 'Cancelled'),
    (APP_ATTENDED, 'Attended'),
    (APP_EXPIRED, 'Expired'),
]

MALE = 'M'
FEMALE = 'F'

GENDERS = [
    (NO_ANSWER, 'Prefer not to answer'),
    (MALE, 'Male'),
    (FEMALE, 'Female'),
]

AMERICAN = 'American Indian or Alaskan Native'
ASIAN = 'Asian / Pacific Islander'
BLACK = 'Black or African American'
HISPANIC = 'Hispanic'
WHITE = 'White / Caucasian'

RACES = [
    (NO_ANSWER, 'Prefer not to answer'),
    (AMERICAN, 'American Indian or Alaskan Native'),
    (ASIAN, 'Asian / Pacific Islander'),
    (BLACK, 'Black or African American'),
    (HISPANIC, 'Hispanic'),
    (WHITE, 'White / Caucasian'),
    (OTHER, 'Multiple ethnicity / Other (Please Specify)'),
]

D_NONE = 'None'
D_VEGETERIAN = 'Vegeterian'
D_VEGAN = 'Vegan'
D_NO_PORK = 'No pork'
D_GLUTEN_FREE = 'Gluten-free'
D_OTHER = 'Others'

DIETS = [
    (D_NONE, 'No requirements'),
    (D_VEGETERIAN, 'Vegeterian'),
    (D_VEGAN, 'Vegan'),
    (D_NO_PORK, 'No pork'),
    (D_GLUTEN_FREE, 'Gluten-free'),
    (D_OTHER, 'Others')
]

NO_JOB = 'No'
OPEN_JOB = 'Maybe'
WANT_JOB = 'Yes'

JOB_INTERESTS = [
    (NO_JOB, 'Not looking for'),
    (OPEN_JOB, 'Open'),
    (WANT_JOB, 'Actively looking for'),
]

JOB_TYPES = [
    ('internship', 'Internship'),
    ('part_time', 'Part-time job'),
    ('full_time', 'Full-time job'),
]

TSHIRT_SIZES = [(size, size) for size in ('XS S M L XL XXL'.split(' '))]
DEFAULT_TSHIRT_SIZE = 'M'

YEARS = [(int(year), year) for year in ('2018 2019 2020 2021 2022 2023 2024 2025'.split(' '))]
YEARS.append((0, 'Not a university student'))
DEFAULT_YEAR = 2018


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/resumes/<filename>
    r = random.SystemRandom()
    randomised = ''.join(r.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    return 'resumes/{}/{}'.format(randomised, filename)


class Ambassador(models.Model):
    # Ambassadors credentials
    user = models.OneToOneField(User, primary_key=True)
    secret_code = models.CharField(max_length=50, unique=True)

    created_date = models.DateTimeField(default=timezone.now)

    # Basic contact informations about ambassador
    origin = models.CharField(max_length=300)
    university = models.CharField(max_length=300)
    phone_number = models.CharField(
        max_length=16,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+#########'. Up to 15 digits allowed."
        )]
    )
    tshirt_size = models.CharField(max_length=3, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)

    def __str__(self):
        return self.user.email

    def convinced(self):
        apps = Application.objects.filter(ambassador=self.user.pk)
        return len(apps)


class Application(models.Model):
    # META
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, primary_key=True)
    invited_by = models.ForeignKey(User, related_name='invited_applications', blank=True, null=True)
    ambassador = models.ForeignKey(Ambassador, blank=True, null=True)

    # When was the application submitted
    submission_date = models.DateTimeField(default=timezone.now)
    # When was the last status update
    status_update_date = models.DateTimeField(blank=True, null=True)
    # Application status
    status = models.CharField(choices=STATUS, default=APP_PENDING,
                              max_length=2)

    # ABOUT YOU
    # Population analysis, optional
    gender = models.CharField(max_length=20, choices=GENDERS, default=NO_ANSWER)

    race = models.CharField(max_length=100, choices=RACES, default=NO_ANSWER)
    other_race = models.CharField(max_length=500, blank=True, null=True)
    # Personal data
    birth_day = models.DateField()

    phone_number = models.CharField(max_length=16,
                                    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                                               message="Phone number must be entered in the format: \
                                                                  '+#########'. Up to 15 digits allowed.")])

    country = models.CharField(max_length=300,blank=True)

    # Where is this person coming from?
    origin = models.CharField(max_length=300)

    # Is this your first hackathon?
    first_timer = models.BooleanField()
    # Why do you want to come to X?
    description = models.TextField(max_length=500)
    # Explain a little bit what projects have you done lately
    projects = models.TextField(max_length=500, blank=True, null=True)

    # Are you looking for a job?
    job_interest = models.CharField(max_length=100, default=WANT_JOB, choices=JOB_INTERESTS)
    job_type = models.CharField(max_length=100, choices=JOB_TYPES, blank=True, null=True)

    # Reimbursement and visa
    reimb = models.BooleanField(default=False)
    reimb_amount = models.FloatField(blank=True, null=True, validators=[
        MinValueValidator(0, "Negative? Really? Please put a positive value")])
    visas = models.BooleanField(default=False)

    # Random questions or let us get to know you better
    hear_about = models.CharField(max_length=200)
    spirit_animal = models.TextField(max_length=1000, blank=True, null=True)
    comment = models.TextField(max_length=1000, blank=True, null=True)

    # Giv me a resume here!
    resume = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    # University
    graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
    university = models.CharField(max_length=300)
    major = models.CharField(max_length=300, blank=True)
    degree = models.CharField(max_length=300, blank=True)

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    # Info for swag and food
    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)
    tshirt_size = models.CharField(max_length=3, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)

    # Parent/Legal guardian information
    guardian_name = models.CharField(verbose_name='Full name of Parent/Legal guardian', max_length=255, blank=True)
    guardian_birth_day = models.DateField(verbose_name='Date of birth of Parent/Legal guardian', null=True, blank=True)

    @classmethod
    def annotate_vote(cls, qs):
        return qs.annotate(vote_avg=Avg('vote__calculated_vote'))

    @property
    def uuid_str(self):
        return str(self.uuid)

    def get_soft_status_display(self):
        text = self.get_status_display()
        if "Not" in text or 'Rejected' in text:
            return "Pending"
        return text

    def __str__(self):
        return self.user.email

    def save(self, **kwargs):
        self.status_update_date = timezone.now()
        super(Application, self).save(**kwargs)

    def under_age(self):
        delta = date.today() - self.birth_day
        if delta < timedelta(days=(18 * 365 + 4)):
            return True
        else:
            return False

    def invite(self, user):
        # We can re-invite someone invited
        if self.status in [APP_CONFIRMED, APP_ATTENDED]:
            raise ValidationError('Application has already answered invite. '
                                  'Current status: %s' % self.status)
        self.status = APP_INVITED
        if not self.invited_by:
            self.invited_by = user
        self.last_invite = timezone.now()
        self.last_reminder = None
        self.status_update_date = timezone.now()
        self.save()

    def last_reminder(self):
        if self.status != APP_INVITED:
            raise ValidationError('Reminder can\'t be sent to non-pending '
                                  'applications')
        self.status_update_date = timezone.now()
        self.status = APP_LAST_REMIDER
        self.save()

    def expire(self):
        self.status_update_date = timezone.now()
        self.status = APP_EXPIRED
        self.save()

    def reject(self, request):
        if self.status == APP_ATTENDED:
            raise ValidationError('Application has already attended. '
                                  'Current status: %s' % self.status)
        self.status = APP_REJECTED
        self.status_update_date = timezone.now()
        self.save()

    def confirm(self):
        if self.status == APP_CANCELLED:
            raise ValidationError('This invite has been cancelled.')
        elif self.status == APP_EXPIRED:
            raise ValidationError('Unfortunately your invite has expired.')
        elif self.status in [APP_INVITED, APP_LAST_REMIDER]:
            self.status = APP_CONFIRMED
            self.status_update_date = timezone.now()
            self.save()
        elif self.status in [APP_CONFIRMED, APP_ATTENDED]:
            return None
        else:
            raise ValidationError('Unfortunately his application hasn\'t been '
                                  'invited [yet]')

    def cancel(self):
        if not self.can_be_cancelled():
            raise ValidationError('Application can\'t be cancelled. Current '
                                  'status: %s' % self.status)
        if self.status != APP_CANCELLED:
            self.status = APP_CANCELLED
            self.status_update_date = timezone.now()
            self.save()
            reimb = getattr(self.user, 'reimbursement', None)
            if reimb:
                reimb.delete()

    def check_in(self):
        self.status = APP_ATTENDED
        self.status_update_date = timezone.now()
        self.save()

    def is_confirmed(self):
        return self.status == APP_CONFIRMED

    def is_cancelled(self):
        return self.status == APP_CANCELLED

    def answered_invite(self):
        return self.status in [APP_CONFIRMED, APP_CANCELLED, APP_ATTENDED]

    def needs_action(self):
        return self.status == APP_INVITED

    def is_pending(self):
        return self.status == APP_PENDING

    def can_be_edit(self):
        return self.status == APP_PENDING and not self.vote_set.exists() and not utils.is_app_closed()

    def is_invited(self):
        return self.status == APP_INVITED

    def is_expired(self):
        return self.status == APP_EXPIRED

    def is_rejected(self):
        return self.status == APP_REJECTED

    def is_attended(self):
        return self.status == APP_ATTENDED

    def is_last_reminder(self):
        return self.status == APP_LAST_REMIDER

    def can_be_cancelled(self):
        return self.status == APP_CONFIRMED or self.status == APP_INVITED or self.status == APP_LAST_REMIDER

    def can_confirm(self):
        return self.status in [APP_INVITED, APP_LAST_REMIDER]

    def is_team_closed(self):
        return self.status in [APP_ATTENDED, APP_EXPIRED, APP_REJECTED, APP_CANCELLED]
