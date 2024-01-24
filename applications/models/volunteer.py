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

GENDERS_ES = [
    (NO_ANSWER, 'Prefiero no responder'),
    (MALE, 'Hombre'),
    (FEMALE, 'Mujer'),
    (NON_BINARY, 'No binario'),
    (GENDER_OTHER, 'Prefiero describirme'),
]

LENGUAGUES_ES = [
("Spanish", "Español"),
("Catalan", "Catalán"),
("English", "Inglés")
]

ATTENDANCE_ES = [
    (0, "Viernes"),
    (1, "Sábado"),
    (2, "Domingo")
]

HEARABOUTUS_ES = [
("Posters", "Posters"),
("Redes Sociales", "Redes Sociales"),
("Mesas en el bar de la FIB","Mesas en el bar de la FIB"),
("Whatsapp, amigos u otras personas","Whatsapp, amigos u otras personas"),
("Web", "Web"),
("Otros", "Otros")
]


DIETS_ES = [
    (D_NONE, 'Sin requerimientos'),
    (D_VEGETERIAN, 'Vegetariano'),
    (D_VEGAN, 'Vegano'),
    (D_GLUTEN_FREE, 'Sin gluten'),
    (D_OTHER, 'Otros')
]

class VolunteerApplication(BaseApplication):

    # gender
    gender = models.CharField(max_length=23, choices=GENDERS_ES, default=NO_ANSWER)

    # diet
    diet = models.CharField(max_length=300, choices=DIETS_ES, default=D_NONE)
    # Where is this person coming from?
    origin = models.CharField(max_length=300)

    # Is this your first hackathon?
    first_timer = models.BooleanField(default=False)

    # Random lenny face
    lennyface = models.CharField(max_length=300, default="-.-")

    #About us
    hear_about_us = models.CharField(max_length=300, choices=HEARABOUTUS_ES, default="")

    # University
    graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
    university = models.CharField(max_length=300)
    degree = models.CharField(max_length=300)

    attendance = MultiSelectField(choices=ATTENDANCE_ES)

    languages = MultiSelectField(choices=LENGUAGUES_ES)
    which_hack = MultiSelectField(choices=PREVIOUS_HACKS)

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
