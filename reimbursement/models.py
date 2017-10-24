# coding=utf-8
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from user.models import User

DEFAULT_REIMBURSEMENT = settings.DEFAULT_REIMBURSEMENT
DEFAULT_CURRENCY = settings.DEFAULT_CURRENCY
DEFAULT_EXPIRACY_DAYS = settings.DEFAULT_EXPIRACY_DAYS

RE_DRAFT = 'D'
RE_VALIDATED = 'V'
RE_ACCEPTED = 'A'
RE_REJECTED = 'R'
RE_EXPIRED = 'X'
RE_FRIEND_VALIDATED = 'FV'
RE_NEEDS_CHANGE = 'NC'

RE_STATUS = [
    (RE_DRAFT, 'Draft'),
    (RE_ACCEPTED, 'Accepted'),
    (RE_REJECTED, 'Rejected'),
    (RE_VALIDATED, 'Ticket validated'),
    (RE_EXPIRED, 'Expired'),
    (RE_FRIEND_VALIDATED, 'Friend validated'),
    (RE_NEEDS_CHANGE, 'Needs change'),
]


class Reimbursement(models.Model):
    application = models.OneToOneField('hackers.Application', primary_key=True)
    status = models.CharField(max_length=2, choices=RE_STATUS,
                              default=RE_DRAFT)

    #
    assigned_money = models.FloatField(null=True, blank=True)
    currency_sign = models.CharField(max_length=3)

    paypal_email = models.EmailField(null=True, blank=True)

    origin_city = models.CharField(max_length=300)
    origin_country = models.CharField(max_length=300)

    reimbursed_by = models.ForeignKey(User, null=True, blank=True)
    expiration_time = models.DateTimeField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    change_reason = models.CharField(max_length=300, null=True, blank=True)

    def check_prices(self):
        price = DEFAULT_REIMBURSEMENT
        currency = DEFAULT_CURRENCY
        try:
            price_t = Reimbursement.objects.filter(
                assigned_money__isnull=False, origin_city=self.origin_city,
                origin_country=self.origin_country) \
                .order_by('-status_update_date') \
                .values('assigned_money', 'currency_sign').first()
            price = price_t['assigned_money']
            currency = price_t['currency_sign']
        except:
            pass

        self.assigned_money = price
        self.currency_sign = currency

    def is_accepted(self):
        return self.status in [RE_ACCEPTED, RE_VALIDATED, RE_FRIEND_VALIDATED, RE_NEEDS_CHANGE]

    def needs_change(self):
        return self.status == RE_NEEDS_CHANGE

    def is_expired(self):
        return self.status == RE_EXPIRED

    def accept(self, user):
        if not self.assigned_money:
            raise ValidationError('Reimbursement can\'t be sent because '
                                  'there\'s no assigned money')

        self.status = RE_ACCEPTED
        self.status_update_date = timezone.now()
        self.reimbursed_by = user
        self.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRACY_DAYS)
        self.save()
