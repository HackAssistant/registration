from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.utils.datetime_safe import datetime

from applications.models import APP_CONFIRMED, Application
from offer.models import Code
from user.models import User


class CheckIn(models.Model):
    application_user = models.ForeignKey(User, related_name="application_user")
    user = models.ForeignKey(User, related_name="user")
    update_time = models.DateTimeField()

    # QR identifier for wristband identification
    qr_identifier = models.CharField(max_length=255, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = datetime.now()
        super(CheckIn, self).save(force_insert, force_update, using,
                                  update_fields)
        app = Application.objects.filter(user=self.application_user).first()
        if app:
            app.check_in()

        # Assign one code per available offer to the user
        if not self.application_user.is_sponsor and not self.application_user.is_mentor and not \
                self.application_user.is_judge and not self.application_user.is_volunteer:
            codes = {c["offer"]: c["id"] for c in
                     Code.objects.filter(user__isnull=True).order_by("-id").values("id", "offer")}
            Code.objects.filter(id__in=list(codes.values())).update(user_id=self.application_user.id)

    def delete(self, using=None, keep_parents=False):
        app = Application.objects.filter(user=self.application_user).first()
        if app:
            app.status = APP_CONFIRMED
            app.save()
        super(CheckIn, self).delete(using, keep_parents)
