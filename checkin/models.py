from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.utils import timezone

from applications.models import APP_CONFIRMED, APP_ATTENDED
from offer.models import Code
from user.models import User


class CheckIn(models.Model):
    hacker = models.OneToOneField('applications.HackerApplication', blank=True, null=True, on_delete=models.CASCADE)
    mentor = models.OneToOneField('applications.MentorApplication', blank=True, null=True, on_delete=models.CASCADE)
    volunteer = models.OneToOneField('applications.VolunteerApplication', blank=True, null=True, on_delete=models.CASCADE)
    sponsor = models.OneToOneField('applications.SponsorApplication', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    update_time = models.DateTimeField()
    # QR identifier for wristband identification
    qr_identifier = models.CharField(max_length=255, null=True)

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
            self.application.save()
            # Assign one code per available offer to the user
            if not self.application.user.is_sponsor and not self.application.user.is_mentor and not \
               self.application.user.is_judge and not self.application.user.is_volunteer:
                codes = {c["offer"]: c["id"] for c in
                         Code.objects.filter(user__isnull=True).order_by("-id").values("id", "offer")}
                Code.objects.filter(id__in=list(codes.values())).update(user_id=self.application.user.id)
        else:
            raise ValueError

    def delete(self, using=None, keep_parents=False):
        app = self.application
        app.status = APP_CONFIRMED
        app.save()
        return super().delete(using, keep_parents)

    def type(self):
        return self.application.user.get_type_display()
