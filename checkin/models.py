from __future__ import unicode_literals

from django.db import models
from register.models import Application

# Create your models here.

class CheckIn(models.Model):
    application = models.OneToOneField('register.Application')

