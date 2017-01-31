from __future__ import unicode_literals

import csv

import os
from django.conf import settings
from django.contrib.auth import models as admin_models
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, F
from django.utils import timezone
from register.emails import sendgrid_send, MailListManager
from register.utils import reverse

# Votes weight
TECH_WEIGHT = 0.2
PERSONAL_WEIGHT = 0.8

# Reimbursement tiers
DEFAULT_REIMBURSEMENT = 100

APP_ACCEPTED = 'A'
APP_PENDING = 'P'
APP_REJECTED = 'R'
APP_INVITED = 'I'
APP_CONFIRMED = 'C'
APP_CANCELLED = 'X'
APP_ATTENDED = 'T'

STATUS = [
    (APP_ACCEPTED, 'Accepted'),
    (APP_PENDING, 'Pending'),
    (APP_REJECTED, 'Rejected'),
    (APP_INVITED, 'Invited'),
    (APP_CONFIRMED, 'Confirmed'),
    (APP_CANCELLED, 'Cancelled'),
    (APP_ATTENDED, 'Attended'),
]


# Create your models here.

def calculate_reimbursement(country):
    with open(os.path.join(settings.BASE_DIR, 'reimbursements.csv')) as reimbursements:
        reader = csv.reader(reimbursements, delimiter=',')
        for row in reader:
            if country in row[0]:
                return int(row[1])

    return DEFAULT_REIMBURSEMENT


class Application(models.Model):
    id = models.TextField(primary_key=True)
    submission_date = models.DateTimeField()
    invitation_date = models.DateTimeField(blank=True, null=True)
    sendgrid_id = models.TextField(default="")
    reimbursement_money = models.IntegerField(blank=True, null=True)

    # Personal data
    name = models.TextField()
    lastname = models.TextField()
    email = models.EmailField()
    graduation = models.DateField()
    university = models.TextField()
    degree = models.TextField(default='Computer Science')
    under_age = models.NullBooleanField()

    # URLs
    github = models.URLField()
    devpost = models.URLField()
    linkedin = models.URLField()
    site = models.URLField()

    # Self improvement
    first_timer = models.NullBooleanField()
    description = models.TextField()
    projects = models.TextField()
    diet = models.TextField()
    tshirt_size = models.CharField(max_length=3, default='M')
    country = models.TextField()
    scholarship = models.NullBooleanField()
    lennyface = models.TextField(default='-.-')

    # Team
    team = models.NullBooleanField()
    teammates = models.TextField(default='None')

    # Needs to be set to true -> else rejected
    authorized_mlh = models.NullBooleanField()
    status = models.CharField(choices=STATUS, default=APP_PENDING, max_length=2)

    # TODO: TEAM EXTERNAL

    def invite(self, request):
        if not request.user.has_perm('register.invite_application'):
            raise ValidationError('User doesn\'t have permission to invite user')
        if self.status != APP_ACCEPTED:
            raise ValidationError('Application needs to be accepted to send. Current status: %s' % self.status)
        self._send_invite(request)
        self.status = APP_INVITED
        self.invitation_date = timezone.now()
        self.save()

    def send_reminder(self, request):
        if not request.user.has_perm('register.invite_application'):
            raise ValidationError('User doesn\'t have permission to invite thus can\'t send reminds neither')
        self._send_reminder(request)

    def is_confirmed(self):
        return self.status == APP_CONFIRMED

    def send_reimbursement(self, request):
        if self.status != APP_INVITED and self.status != APP_CONFIRMED:
            raise ValidationError('Application can\'t be reimbursed as it hasn\'t been invited yet')
        if not self.scholarship:
            raise ValidationError('Application didn\'t ask for reimbursement')
        if not self.reimbursement_money:
            self.reimbursement_money = calculate_reimbursement(self.country)

        self._send_reimbursement(request)
        self.save()

    def confirm(self, cancellation_url):
        if self.status != APP_INVITED and self.status != APP_CONFIRMED:
            raise ValidationError('Application hasn\'t been invited yet')
        if self.status != APP_CONFIRMED:
            m = MailListManager()
            m.add_applicant_to_list(self, m.W17_GENERAL_LIST_ID)
            if self.scholarship:
                m.add_applicant_to_list(self, m.W17_TRAVEL_REIMB_LIST_ID)
            self._send_confirmation_ack(cancellation_url)
            self.status = APP_CONFIRMED
            self.save()

    def can_be_cancelled(self):
        return self.status == APP_CONFIRMED or self.status == APP_INVITED

    def cancel(self):
        if not self.can_be_cancelled():
            raise ValidationError('Application can\'t be cancelled. Current status: %s' % self.status)
        if self.status != APP_CANCELLED:
            self.status = APP_CANCELLED
            self.save()
            m = MailListManager()
            m.remove_recipient_from_list(self.sendgrid_id, m.W17_GENERAL_LIST_ID)
            if self.scholarship:
                m.remove_recipient_from_list(self.sendgrid_id, m.W17_TRAVEL_REIMB_LIST_ID)

    def confirmation_url(self, request=None):
        return reverse('confirm_app', kwargs={'token': self.id}, request=request)

    def cancelation_url(self, request=None):
        return reverse('cancel_app', kwargs={'token': self.id}, request=request)

    def _send_invite(self, request):
        sendgrid_send(
            [self.email],
            "[HackUPC] You are invited!",
            {'%name%': self.name,
             '%confirmation_url%': self.confirmation_url(request),
             '%cancellation_url%': self.cancelation_url(request)},
            '513b4761-9c40-4f54-9e76-225c2835b529'
        )

    def _send_reminder(self, request):
        sendgrid_send(
            [self.email],
            "[HackUPC] Missing answer",
            {'%name%': self.name,
             '%confirmation_url%': self.confirmation_url(request),
             '%cancellation_url%': self.cancelation_url(request)},
            '3150c49d-0b5d-4e75-bf78-0bef3a79bbdc'

        )

    def _send_confirmation_ack(self, cancellation_url):
        sendgrid_send(
            [self.email],
            "[HackUPC] You confirmed your attendance!",
            {'%name%': self.name,
             '%token%': self.id,
             '%cancellation_url%': cancellation_url},
            'c4d4d758-974f-437b-af9a-d8532f96d670'
        )

    def _send_reimbursement(self, request):
        sendgrid_send(
            [self.email],
            "[HackUPC] Reimbursement granted",
            {'%name%': self.name,
             '%token%': self.id,
             '%money%': self.reimbursement_money,
             '%country%': self.country,
             '%confirmation_url%': self.confirmation_url(request),
             '%cancellation_url%': self.cancelation_url(request)},
            '06d613dd-cf70-427b-ae19-6cfe7931c193',
            from_email='HackUPC Reimbursements Team <reimbursements@hackupc.com>'
        )

    class Meta:
        permissions = (
            ("accept_application", "Can accept applications"),
            ("invite_application", "Can invite applications"),
            ("attended_application", "Can mark as attended applications"),
            ("reject_application", "Can reject applications"),
            ("force_status", "Can force status application"),
        )


VOTES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10'),
)


class Vote(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(admin_models.User)
    tech = models.IntegerField(choices=VOTES, null=True)
    personal = models.IntegerField(choices=VOTES, null=True)
    calculated_vote = models.FloatField(null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        We are overriding this in order to standarize each review vote with the new vote.
        Also we store a calculated vote for each vote so that we don't need to do it later.

        Thanks to Django awesomeness we do all the calculations with only 3 queries to the database.
        2 selects and 1 update. The performance is way faster than I thought. If improvements need to be done
        using a better DB than SQLite should increase performance. As long as the database can handle aggregations
        efficiently this will be good.

        By casassg
        """
        super(Vote, self).save(force_insert, force_update, using, update_fields)

        # only recalculate when values are different than None
        if not self.personal or not self.tech:
            return

        # Retrieve averages
        avgs = admin_models.User.objects.filter(id=self.user_id).aggregate(tech=Avg('vote__tech'),
                                                                           pers=Avg('vote__personal'))
        p_avg = round(avgs['pers'], 2)
        t_avg = round(avgs['tech'], 2)

        # Calculate standard deviation for each scores
        sds = admin_models.User.objects.filter(id=self.user_id).aggregate(
            tech=Avg((F('vote__tech') - t_avg) * (F('vote__tech') - t_avg)),
            pers=Avg((F('vote__personal') - p_avg) * (F('vote__personal') - p_avg)))

        # Alternatively, if standard deviation is 0.0, set it as 1.0 to avoid division by 0.0 in the update statement
        p_sd = round(sds['pers'], 2) or 1.0
        t_sd = round(sds['tech'], 2) or 1.0

        # Apply standarization. Standarization formula:
        # x(new) = (x - u)/o
        # where u is the mean and o is the standard deviation
        #
        # See this: http://www.dataminingblog.com/standardization-vs-normalization/
        Vote.objects.filter(user=self.user).update(
            calculated_vote=
            PERSONAL_WEIGHT * (F('personal') - p_avg) / p_sd +
            TECH_WEIGHT * (F('tech') - t_avg) / t_sd
        )

    class Meta:
        unique_together = ('application', 'user')
