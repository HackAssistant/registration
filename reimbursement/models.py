from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import models as admin_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from register import models as r_models
from register.models import Application

RE_NOT_SENT = 'P'
RE_SENT = 'S'

RE_STATUS = [
    (RE_NOT_SENT, 'Not sent'),
    (RE_SENT, 'Sent'),
]


class Reimbursement(models.Model):
    application = models.OneToOneField(Application, primary_key=True)
    assigned_money = models.FloatField(null=True, blank=True)
    origin_city = models.CharField(max_length=300)
    origin_country = models.CharField(max_length=300)
    status = models.CharField(max_length=2, choices=RE_STATUS, default=RE_NOT_SENT)
    reimbursed_by = models.ForeignKey(admin_models.User, null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    status_update_date = models.DateTimeField(default=timezone.now)

    def check_prices(self):
        price = settings.DEFAULT_REIMBURSEMENT
        try:
            price_t = Reimbursement.objects.filter(assigned_money__isnull=False, origin_city=self.origin_city,
                                                   origin_country=self.origin_country) \
                .order_by('-status_update_date').values('assigned_money').first()
            price = price_t['assigned_money']
        except:
            pass

        self.assigned_money = price

    def send(self, user):
        if self.application.status not in [r_models.APP_INVITED, r_models.APP_CONFIRMED, r_models.APP_LAST_REMIDER]:
            raise ValidationError('Application can\'t be reimbursed as it hasn\'t been invited yet')
        self.status = RE_SENT
        self.status_update_date = timezone.now()
        self.reimbursed_by = user
        self.save()

    class Meta:
        permissions = (
            ("reimburse", "Can assign reimbursements"),
        )
