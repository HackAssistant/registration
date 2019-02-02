from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.utils.datetime_safe import datetime
from django.utils import timezone
from applications.models import APP_CONFIRMED, Application
from user.models import User

SUBJECTS = (
    ('arrived', 'Hacker arrival'),
    ('sat_lunch', 'Saturday lunch'),
    ('sat_dinner', 'Saturday dinner'),
    ('sun_lunch', 'Sunday lunch'),
)


class CheckIn(models.Model):
    check_type = models.CharField(
        max_length=10,
        choices=SUBJECTS,
    )
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User)
    update_time = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = timezone.now()
        super(CheckIn, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def delete(self, using=None, keep_parents=False):
        if self.check_type == 'arrived':
            self.application.status = APP_CONFIRMED
            self.application.save()
        super(CheckIn, self).delete(using, keep_parents)
