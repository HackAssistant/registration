from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.utils.datetime_safe import datetime

from applications.models import APP_CONFIRMED, APP_ATTENDED
from user.models import User


class CheckIn(models.Model):
    hacker = models.OneToOneField('applications.HackerApplication', null=True)
    mentor = models.OneToOneField('applications.MentorApplication', null=True)
    volunteer = models.OneToOneField('applications.VolunteerApplication', null=True)
    sponsor = models.OneToOneField('applications.SponsorApplication', null=True)
    user = models.ForeignKey(User)
    update_time = models.DateTimeField()

    @property
    def application(self):
        if self.hacker:
            return self.hacker
        if self.mentor:
            return self.mentor
        if self.volunteer:
            return self.volunteer
        if self.sponsor:
            return self.sponsor
        return None

    def set_application(self, app):
        if app.user.is_hacker():
            self.hacker = app
        elif app.user.is_volunteer():
            self.volunteer = app
        elif app.user.is_mentor():
            self.mentor = app
        elif app.user.is_sponsor():
            self.sponsor = app
        else:
            raise ValueError

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if (self.hacker and self.sponsor is None and self.volunteer is None and self.mentor is None) or \
           (self.hacker is None and self.sponsor and self.volunteer is None and self.mentor is None) or \
           (self.hacker is None and self.sponsor is None and self.volunteer and self.mentor is None) or \
           (self.hacker is None and self.sponsor is None and self.volunteer is None and self.mentor):
            self.update_time = datetime.now()
            super(CheckIn, self).save(force_insert, force_update, using,
                                      update_fields)
            self.application.status = APP_ATTENDED
        else:
            raise ValueError

    def delete(self, using=None, keep_parents=False):
        self.application.status = APP_CONFIRMED
        self.application.save()
        super(CheckIn, self).delete(using, keep_parents)

    def type(self):
        return self.application.user.get_type_display()
