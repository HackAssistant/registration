# coding=utf-8
from __future__ import unicode_literals

from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import models as admin_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from register import models as r_models
from register.models import Application

RE_NOT_SENT = 'P'
RE_SENT = 'S'
RE_ACCEPTED = 'A'
RE_FRIEND_ACCEPTED = 'FA'
RE_NEEDS_CHANGE = 'NC'

RE_STATUS = [
    (RE_NOT_SENT, 'Draft'),
    (RE_SENT, 'Sent'),
    (RE_ACCEPTED, 'Accepted'),
    (RE_FRIEND_ACCEPTED, 'Friend accepted'),
    (RE_NEEDS_CHANGE, 'Needs change'),
]


class Reimbursement(models.Model):
    application = models.OneToOneField(Application, primary_key=True)
    assigned_money = models.FloatField(null=True, blank=True)
    paypal_email = models.EmailField(null=True, blank=True)
    currency_sign = models.CharField(max_length=3, default="€")
    origin_city = models.CharField(max_length=300)
    origin_country = models.CharField(max_length=300)
    status = models.CharField(max_length=2, choices=RE_STATUS,
                              default=RE_NOT_SENT)
    reimbursed_by = models.ForeignKey(admin_models.User, null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    status_update_date = models.DateTimeField(default=timezone.now)
    change_reason = models.CharField(max_length=300, null=True, blank=True)

    def check_prices(self):
        price = settings.DEFAULT_REIMBURSEMENT
        try:
            price_t = Reimbursement.objects.filter(
                assigned_money__isnull=False, origin_city=self.origin_city,
                origin_country=self.origin_country) \
                .order_by('-status_update_date') \
                .values('assigned_money').first()
            price = price_t['assigned_money']
        except:
            pass

        self.assigned_money = price

    def is_sent(self):
        return self.status == RE_SENT

    def is_accepted(self):
        return self.status == RE_ACCEPTED

    def friend_accepted(self):
        return self.status == RE_FRIEND_ACCEPTED

    def needs_change(self):
        return self.status == RE_NEEDS_CHANGE

    def is_expired(self):
        return self.expiration_time() <= datetime.today() and self.status in [RE_SENT, RE_NEEDS_CHANGE]

    def expiration_time(self):
        return self.status_update_date + timedelta(days=5)

    def send(self, user):
        if self.application.status not in [r_models.APP_INVITED,
                                           r_models.APP_CONFIRMED,
                                           r_models.APP_LAST_REMIDER]:
            raise ValidationError('Application can\'t be reimbursed as it '
                                  'hasn\'t been invited yet')
        if not self.assigned_money:
            raise ValidationError('Reimbursement can\'t be sent because '
                                  'there\'s no assigned money')

        self.status = RE_SENT
        self.status_update_date = timezone.now()
        self.reimbursed_by = user
        self.save()

    def get_form_url(self):
        return 'https://%s.typeform.com/to/%s' % (
            settings.REIMBURSEMENT_APP.get('typeform_user'),
            settings.REIMBURSEMENT_APP.get('typeform_form'))

    class Meta:
        permissions = (
            ("reimburse", "Can assign reimbursements"),
        )
