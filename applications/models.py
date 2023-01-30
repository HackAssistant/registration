from __future__ import unicode_literals

import json
import os
import uuid as uuid
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.forms import model_to_dict
from django.utils import timezone
from multiselectfield import MultiSelectField

from app import utils, hackathon_variables
from user.models import User, BlacklistUser
from user import models as userModels
from applications.validators import validate_file_extension

APP_PENDING = 'P'
APP_REJECTED = 'R'
APP_INVITED = 'I'
APP_LAST_REMIDER = 'LR'
APP_CONFIRMED = 'C'
APP_CANCELLED = 'X'
APP_ATTENDED = 'A'
APP_EXPIRED = 'E'
APP_DUBIOUS = 'D'
APP_INVALID = 'IV'
APP_BLACKLISTED = 'BL'

PENDING_TEXT = 'Under review'
DUBIOUS_TEXT = 'Dubious'
BLACKLIST_TEXT = 'Blacklisted'
STATUS = [
    (APP_PENDING, PENDING_TEXT),
    (APP_REJECTED, 'Wait listed'),
    (APP_INVITED, 'Invited'),
    (APP_LAST_REMIDER, 'Last reminder'),
    (APP_CONFIRMED, 'Confirmed'),
    (APP_CANCELLED, 'Cancelled'),
    (APP_ATTENDED, 'Attended'),
    (APP_EXPIRED, 'Expired'),
    (APP_DUBIOUS, DUBIOUS_TEXT),
    (APP_INVALID, 'Invalid'),
    (APP_BLACKLISTED, BLACKLIST_TEXT)
]

NO_ANSWER = 'NA'
MALE = 'M'
FEMALE = 'F'
NON_BINARY = 'NB'
GENDER_OTHER = 'X'

GENDERS = [
    (NO_ANSWER, 'Prefer not to answer'),
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (NON_BINARY, 'Non-binary'),
    (GENDER_OTHER, 'Prefer to self-describe'),
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

T_XXS = 'XXS'
T_XS = 'XS'
T_S = 'S'
T_M = 'M'
T_L = 'L'
T_XL = 'XL'
T_XXL = 'XXL'
T_XXXL = 'XXXL'

TSHIRT_SIZES = [
    (T_XS, "Unisex - XS"),
    (T_S, "Unisex - S"),
    (T_M, "Unisex - M"),
    (T_L, "Unisex - L"),
    (T_XL, "Unisex - XL"),
    (T_XXL, "Unisex - XXL"),
    (T_XXXL, "Unisex - XXXL"),
]

DEFAULT_TSHIRT_SIZE = T_M

ATTENDANCE = [
    (0, "Friday"),
    (1, "Saturday"),
    (2, "Sunday")
]

HACK_NAME = getattr(hackathon_variables, 'HACKATHON_NAME', "HackAssistant")
EXTRA_NAME = [' 2016 Fall', ' 2016 Winter', ' 2017 Fall', ' 2017 Winter', ' 2018', ' 2019', '2021']
PREVIOUS_HACKS = [(i, HACK_NAME + EXTRA_NAME[i]) for i in range(0, len(EXTRA_NAME))]

YEARS = [(int(size), size) for size in ('2020 2021 2022 2023 2024 2025 2026 2027'.split(' '))]
DEFAULT_YEAR = datetime.now().year + 1

ENGLISH_LEVEL = [(i, str(i)) for i in range(1, 5 + 1)]


def resume_path_hackers(instance, filename):
    (_, ext) = os.path.splitext(filename)
    return 'resumes_hackers/{}_{}{}'.format(instance.user.name, instance.uuid, ext)


def resume_path_mentors(instance, filename):
    (_, ext) = os.path.splitext(filename)
    return 'resumes_mentors/{}_{}{}'.format(instance.user.name, instance.uuid, ext)


class BaseApplication(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name='%(class)s_application', primary_key=True, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, related_name='%(class)s_invited_applications', blank=True, null=True,
                                   on_delete=models.SET_NULL)

    # When was the application submitted
    submission_date = models.DateTimeField(default=timezone.now)

    # When was the last status update
    status_update_date = models.DateTimeField(blank=True, null=True)

    # Application status
    status = models.CharField(choices=STATUS,
                              default=APP_PENDING,
                              max_length=2)

    # ABOUT YOU
    # Population analysis, optional
    gender = models.CharField(max_length=23, choices=GENDERS, default=NO_ANSWER)
    other_gender = models.CharField(max_length=50, blank=True, null=True)

    # Personal data (asking here because we don't want to ask birthday)
    under_age = models.BooleanField()

    phone_number = models.CharField(blank=True, null=True, max_length=16,
                                    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                                               message="Phone number must be entered in the format: \
                                                                  '+#########'. Up to 15 digits allowed.")])

    # Info for swag and food
    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)
    tshirt_size = models.CharField(max_length=5, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            dict = args[0]['dict']
        except Exception:
            dict = None
        if dict is not None:
            for key in dict:
                atr = getattr(self, key, 'NOT_EXIST')
                if atr != 'NOT_EXIST':
                    setattr(self, key, dict[key])

    def __str__(self):
        return self.user.email

    @property
    def uuid_str(self):
        return str(self.uuid)

    def get_soft_status_display(self):
        text = self.get_status_display()
        if DUBIOUS_TEXT == text or BLACKLIST_TEXT == text:
            return PENDING_TEXT
        return text

    def save(self, **kwargs):
        self.status_update_date = timezone.now()
        super(BaseApplication, self).save(**kwargs)

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

    def can_be_edit(self, app_type='H'):
        return self.status == APP_PENDING

    def is_invited(self):
        return self.status == APP_INVITED

    def is_expired(self):
        return self.status == APP_EXPIRED

    def is_rejected(self):
        return self.status == APP_REJECTED

    def is_invalid(self):
        return self.status == APP_INVALID

    def is_attended(self):
        return self.status == APP_ATTENDED

    def is_last_reminder(self):
        return self.status == APP_LAST_REMIDER

    def is_dubious(self):
        return self.status == APP_DUBIOUS

    def can_be_cancelled(self):
        return self.status == APP_CONFIRMED or self.status == APP_INVITED or self.status == APP_LAST_REMIDER

    def can_confirm(self):
        return self.status in [APP_INVITED, APP_LAST_REMIDER]

    def can_be_invited(self):
        return self.status in [APP_INVITED, APP_LAST_REMIDER, APP_CANCELLED, APP_PENDING, APP_EXPIRED, APP_REJECTED,
                               APP_INVALID]

    def can_join_team(self):
        return self.user.type == userModels.USR_HACKER and self.status in [APP_PENDING, APP_LAST_REMIDER, APP_DUBIOUS]

    def check_in(self):
        self.status = APP_ATTENDED
        self.status_update_date = timezone.now()
        self.save()

    def move_to_pending(self):
        self.status = APP_PENDING
        self.status_update_date = timezone.now()
        self.save()

    def reject(self):
        if self.status == APP_ATTENDED:
            raise ValidationError('Application has already attended. '
                                  'Current status: %s' % self.status)
        self.status = APP_REJECTED
        self.status_update_date = timezone.now()
        self.save()

    def invite(self, user, online=False):
        # We can re-invite someone invited
        if self.status in [APP_CONFIRMED, APP_ATTENDED]:
            raise ValidationError('Application has already answered invite. '
                                  'Current status: %s' % self.status)
        self.status = APP_INVITED
        if not self.invited_by:
            self.invited_by = user
        if online:
            self.online = online
        self.last_invite = timezone.now()
        self.last_reminder = None
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


class _HackerMentorVolunteerApplication(models.Model):
    class Meta:
        abstract = True

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


class _HackerMentorApplication(models.Model):
    class Meta:
        abstract = True

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    # Hacker will assist face-to-face or online
    online = models.BooleanField(default=False)


class _VolunteerMentorApplication(models.Model):
    class Meta:
        abstract = True

    english_level = models.IntegerField(default=0, null=False, choices=ENGLISH_LEVEL)
    which_hack = MultiSelectField(choices=PREVIOUS_HACKS, null=True, blank=True)


class _VolunteerMentorSponsorApplication(models.Model):
    class Meta:
        abstract = True

    attendance = MultiSelectField(choices=ATTENDANCE)


class HackerApplication(
    BaseApplication,
    _HackerMentorVolunteerApplication,
    _HackerMentorApplication
):
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
        return self.status in [APP_PENDING, APP_DUBIOUS] and not self.vote_set.exists() and not utils.is_app_closed(app_type)


class MentorApplication(
    BaseApplication,
    _HackerMentorApplication,
    _HackerMentorVolunteerApplication,
    _VolunteerMentorApplication,
    _VolunteerMentorSponsorApplication
):
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

class VolunteerApplication(
    BaseApplication,
    _VolunteerMentorSponsorApplication,
    _VolunteerMentorApplication,
    _HackerMentorVolunteerApplication
):
    cool_skill = models.CharField(max_length=100, null=False)
    first_time_volunteer = models.BooleanField()
    quality = models.CharField(max_length=150, null=False)
    weakness = models.CharField(max_length=150, null=False)
    fav_movie = models.CharField(max_length=60, null=True, blank=True)
    friends = models.CharField(max_length=100, null=True, blank=True)
    night_shifts = models.BooleanField()
    hobbies = models.CharField(max_length=150, null=False)

    def can_be_edit(self, app_type="V"):
        return self.status in [APP_PENDING, APP_DUBIOUS] and not utils.is_app_closed(app_type)

class SponsorApplication(
    _VolunteerMentorSponsorApplication,
):
    name = models.CharField(
        verbose_name='Full name',
        max_length=255,
    )
    # When was the application submitted
    submission_date = models.DateTimeField(default=timezone.now)

    # When was the last status update
    status_update_date = models.DateTimeField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, related_name='%(class)s_application', null=True, on_delete=models.SET_NULL)
    # Application status
    status = models.CharField(choices=STATUS,
                              default=APP_CONFIRMED,
                              max_length=2)
    phone_number = models.CharField(blank=True, null=True, max_length=16,
                                    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                                               message="Phone number must be entered in the format: \
                                                                          '+#########'. Up to 15 digits allowed.")])

    # Info for swag and food
    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)
    tshirt_size = models.CharField(max_length=5, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)
    position = models.CharField(max_length=50, null=False)

    email = models.EmailField(verbose_name='email', max_length=255, null=True)

    @property
    def uuid_str(self):
        return str(self.uuid)

    def __str__(self):
        return self.name + ' from ' + self.user.name

    def save(self, **kwargs):
        self.status_update_date = timezone.now()
        super(SponsorApplication, self).save(**kwargs)

    def check_in(self):
        self.status = APP_ATTENDED
        self.status_update_date = timezone.now()
        self.save()

    class META:
        unique_together = [['name', 'user']]


class DraftApplication(models.Model):
    content = models.CharField(max_length=7000)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def save_dict(self, d):
        self.content = json.dumps(d)

    def get_dict(self):
        return json.loads(self.content)

    @staticmethod
    def create_draft_application(instance):
        dict = model_to_dict(instance)
        for key in ['user', 'invited_by', 'submission_date', 'status_update_date', 'status', 'resume']:
            dict.pop(key, None)
        d = DraftApplication()
        d.user_id = instance.user_id
        d.save_dict(dict)
        d.save()


class AcceptedResume(models.Model):
    application = models.OneToOneField(HackerApplication, primary_key=True, on_delete=models.CASCADE)
    accepted = models.BooleanField()
