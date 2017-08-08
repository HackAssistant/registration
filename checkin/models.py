from __future__ import unicode_literals

from django.contrib.auth import models as admin_models
from django.db import models
# Create your models here.
from django.utils.datetime_safe import datetime

from register.models import APP_CONFIRMED


class CheckIn(models.Model):
    application = models.ForeignKey('register.Application')
    user = models.ForeignKey(admin_models.User)
    update_time = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = datetime.now()
        super(CheckIn, self).save(force_insert, force_update, using,
                                  update_fields)

    def delete(self, using=None, keep_parents=False):
        self.application.status = APP_CONFIRMED
        self.application.save()
        super(CheckIn, self).delete(using, keep_parents)

    class Meta:
        permissions = (
            ("check_in", "Can checkin applications"),
        )
