from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from applications.models import APP_CONFIRMED, APP_ATTENDED
from user.models import User


class CheckIn(models.Model):
    hacker = models.OneToOneField('applications.HackerApplication', null=True, on_delete=models.CASCADE)
    mentor = models.OneToOneField('applications.MentorApplication', null=True, on_delete=models.CASCADE)
    volunteer = models.OneToOneField('applications.VolunteerApplication', null=True, on_delete=models.CASCADE)
    sponsor = models.OneToOneField('applications.SponsorApplication', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    update_time = models.DateTimeField()

    @property
    def application(self):
        if self.hacker_id:
            return self.hacker
        if self.mentor_id:
            return self.mentor
        if self.volunteer_id:
            return self.volunteer
        if self.sponsor_id:
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
            self.update_time = timezone.now()
            super(CheckIn, self).save(force_insert, force_update, using,
                                      update_fields)
            self.application.status = APP_ATTENDED
        else:
            raise ValueError

    def delete(self, using=None, keep_parents=False):
        app = self.application
        app.status = APP_CONFIRMED
        app.save()
        return super(CheckIn, self).delete(using, keep_parents)

    def type(self):
        return self.application.user.get_type_display()
