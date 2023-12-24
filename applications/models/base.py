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
from .CONSTANTS import *


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

    def get_diet_color(self):
        colors = {
            D_NONE: 'white',
            D_VEGETERIAN: '#7ABE6F',
        }
        return colors.get(self.diet, '#42A2CB')

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


# class _HackerMentorVolunteerApplication(models.Model):
#     class Meta:
#         abstract = True
#
#     # Where is this person coming from?
#     origin = models.CharField(max_length=300)
#
#     # Is this your first hackathon?
#     first_timer = models.BooleanField(default=False)
#
#     # Random lenny face
#     lennyface = models.CharField(max_length=300, default='-.-')
#
#     # University
#     graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
#     university = models.CharField(max_length=300)
#     degree = models.CharField(max_length=300)
#
#
# class _HackerMentorApplication(models.Model):
#     class Meta:
#         abstract = True
#
#     # URLs
#     github = models.URLField(blank=True, null=True)
#     devpost = models.URLField(blank=True, null=True)
#     linkedin = models.URLField(blank=True, null=True)
#     site = models.URLField(blank=True, null=True)
#
#     # Hacker will assist face-to-face or online
#     online = models.BooleanField(default=False)
#
#
# class _VolunteerMentorApplication(models.Model):
#     class Meta:
#         abstract = True
#
#     english_level = models.IntegerField(default=0, null=False, choices=ENGLISH_LEVEL)
#     which_hack = MultiSelectField(choices=PREVIOUS_HACKS, null=True, blank=True)
#
#
# class _VolunteerMentorSponsorApplication(models.Model):
#     class Meta:
#         abstract = True
#
#     attendance = MultiSelectField(choices=ATTENDANCE)
#
#
#
#
#
