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

from .base import *


class VolunteerApplication(BaseApplication):
    # Where is this person coming from?
    origin = models.CharField(max_length=300)

    # Is this your first hackathon?
    first_timer = models.BooleanField(default=False)

    # Random lenny face
    lennyface = models.CharField(max_length=300, default="-.-")

    # University
    graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
    university = models.CharField(max_length=300)
    degree = models.CharField(max_length=300)

    attendance = MultiSelectField(choices=ATTENDANCE)

    english_level = models.IntegerField(default=0, null=False, choices=ENGLISH_LEVEL)
    which_hack = MultiSelectField(choices=PREVIOUS_HACKS, null=True, blank=True)

    cool_skill = models.CharField(max_length=100, null=False)
    first_time_volunteer = models.BooleanField()
    quality = models.CharField(max_length=150, null=False)
    weakness = models.CharField(max_length=150, null=False)
    fav_movie = models.CharField(max_length=60, null=True, blank=True)
    friends = models.CharField(max_length=100, null=True, blank=True)
    pronouns = models.CharField(max_length=100, null=True, blank=True)
    night_shifts = models.BooleanField(null=True)
    hobbies = models.CharField(max_length=150, null=False)
    volunteer_motivation = models.CharField(max_length=500)

    def can_be_edit(self, app_type="V"):
        return self.status in [APP_PENDING, APP_DUBIOUS] and not utils.is_app_closed(
            app_type
        )
