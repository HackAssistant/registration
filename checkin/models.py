from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.utils.datetime_safe import datetime

from applications.models import APP_CONFIRMED, APP_ATTENDED
from user.models import User


class CheckIn(models.Model):
    application = models.OneToOneField('applications.Application')
    user = models.ForeignKey(User)
    update_time = models.DateTimeField()

    # QR identifier for wristband identification
    qr_identifier = models.CharField(max_length=255, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = datetime.now()
        super(CheckIn, self).save(force_insert, force_update, using,
                                  update_fields)
        self.application.status = APP_ATTENDED

    def delete(self, using=None, keep_parents=False):
        self.application.status = APP_CONFIRMED
        self.application.save()
        super(CheckIn, self).delete(using, keep_parents)
