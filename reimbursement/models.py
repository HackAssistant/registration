# coding=utf-8
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from user.models import User

DEFAULT_REIMBURSEMENT_AMOUNT = settings.DEFAULT_REIMBURSEMENT_AMOUNT
DEFAULT_EXPIRACY_DAYS = settings.REIMBURSEMENT_EXPIRACY_DAYS

RE_DRAFT = 'D'
RE_WAITLISTED = 'W'
RE_PEND_TICKET = 'PT'
RE_PEND_APPROVAL = 'PA'
RE_APPROVED = 'A'
RE_FRIEND_SUBMISSION = 'FS'

RE_STATUS = [
    (RE_DRAFT, 'Pending review'),
    (RE_WAITLISTED, 'Wait listed'),
    (RE_PEND_TICKET, 'Pending ticket submission'),
    (RE_PEND_APPROVAL, 'Pending ticket approval'),
    (RE_APPROVED, 'Ticket approved'),
    (RE_FRIEND_SUBMISSION, 'Friend submission'),
]


def check_friend_emails(friend_emails):
    emails = friend_emails.replace(' ', '').split(',')
    for email in emails:
        try:
            user = User.objects.get(email=email)
        except:
            raise Exception('%s is not a registered hacker' % email)

        try:
            if user.reimbursement and not user.reimbursement.status == RE_PEND_TICKET:
                raise Exception('%s doesn\'t have a correct reimbursement' % email)
            if not user.reimbursement:
                raise Exception('%s didn\'t ask for reimbursement' % email)
        except:
            raise Exception('%s didn\'t ask for reimbursement' % email)


class Reimbursement(models.Model):
    # Admin controlled
    assigned_money = models.FloatField()
    reimbursement_money = models.FloatField(null=True, blank=True)
    public_comment = models.CharField(max_length=300, null=True, blank=True)

    # User controlled
    paypal_email = models.EmailField(null=True, blank=True)
    venmo_user = models.CharField(max_length=40, null=True, blank=True)
    receipt = models.FileField(null=True, blank=True, upload_to='receipt', )
    multiple_hackers = models.BooleanField(default=False)
    friend_emails = models.CharField(null=True, blank=True, max_length=400)
    origin_city = models.CharField(max_length=300)
    origin_country = models.CharField(max_length=300)

    # If a friend submitted receipt
    friend_submission = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='friend_submissions',
                                          null=True, blank=True)

    # Meta
    hacker = models.OneToOneField('user.User', primary_key=True)
    reimbursed_by = models.ForeignKey(User, null=True, blank=True, related_name='reimbursements_made')
    expiration_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(default=timezone.now)
    creation_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=RE_STATUS,
                              default=RE_DRAFT)

    @property
    def max_assignable_money(self):
        if self.friend_submission:
            return 0
        if not self.multiple_hackers:
            return self.assigned_money
        return sum([reimb.assigned_money for reimb in self.friend_submissions]) + self.assigned_money

    @property
    def friend_emails_list(self):
        if not self.multiple_hackers:
            return None
        return self.friend_emails.replace(' ', '').split(',')

    @property
    def timeleft_expiration(self):
        if not self.expiration_time:
            return None
        return self.expiration_time - timezone.now()

    @property
    def expired(self):
        return timezone.now() > self.expiration_time and self.status == RE_PEND_TICKET

    def generate_draft(self, application):
        price = DEFAULT_REIMBURSEMENT_AMOUNT
        try:
            price_t = Reimbursement.objects.filter(
                origin_city=self.origin_city,
                origin_country=self.origin_country) \
                .order_by('-creation_time') \
                .values('assigned_money').first()
            price = price_t['assigned_money']
        except:
            pass

        self.assigned_money = price
        self.origin_country = application.origin_country
        self.origin_city = application.origin_city
        self.hacker = application.user
        self.save()

    def send(self, user):
        if not self.assigned_money:
            raise ValidationError('Reimbursement can\'t be sent because '
                                  'there\'s no assigned money')

        self.status = RE_PEND_TICKET
        self.status_update_date = timezone.now()
        self.reimbursed_by = user
        self.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRACY_DAYS)
        self.save()

    def is_sent(self):
        return self.status in [RE_PEND_APPROVAL, RE_PEND_TICKET, ]

    def is_draft(self):
        return self.status == RE_DRAFT

    def waitlisted(self):
        return self.status == RE_WAITLISTED

    def pending_receipt(self):
        return self.status in RE_PEND_TICKET

    def reject_receipt(self, comment):
        self.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRACY_DAYS)
        self.public_comment = comment
        if self.multiple_hackers:
            for reimb in self.friend_submissions:
                reimb.friend_submission = None
                reimb.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRACY_DAYS)
                reimb.public_comment = 'Your friend %s submission has not been accepted' % self.hacker.get_full_name()
                reimb.status = RE_PEND_TICKET
                reimb.save()

    def submit_receipt(self):
        self.status = RE_PEND_APPROVAL
        if self.multiple_hackers:
            for reimb in Reimbursement.objects.filter(hacker__email__in=self.friend_emails_list):
                reimb.friend_submission = self
                reimb.status = RE_FRIEND_SUBMISSION
                reimb.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = timezone.now()
        super(Reimbursement, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)
