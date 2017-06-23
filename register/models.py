from __future__ import unicode_literals

import csv
import os

from django.conf import settings
from django.contrib.auth import models as admin_models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, F
from django.utils import timezone

from app.emails import sendgrid_send, MailListManager
from app.utils import reverse

# Votes weight
TECH_WEIGHT = 0.2
PERSONAL_WEIGHT = 0.8

# Reimbursement tiers
DEFAULT_REIMBURSEMENT = 100

APP_STARTED = 'S'
APP_COMPLETED = 'P'
APP_REJECTED = 'R'
APP_INVITED = 'I'
APP_CONFIRMED = 'C'
APP_CANCELLED = 'X'
APP_ATTENDED = 'T'
APP_EXPIRED = 'E'

STATUS = [
    (APP_STARTED, 'Started'),
    (APP_COMPLETED, 'Completed'),
    (APP_REJECTED, 'Rejected'),
    (APP_INVITED, 'Invited'),
    (APP_CONFIRMED, 'Confirmed'),
    (APP_CANCELLED, 'Cancelled'),
    (APP_ATTENDED, 'Attended'),
    (APP_EXPIRED, 'Expired'),
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
    last_reminder = models.DateTimeField(blank=True, null=True)
    sendgrid_id = models.TextField(default="")

    # Personal data
    name = models.TextField()
    lastname = models.TextField()
    email = models.EmailField()
    country = models.TextField()
    under_age = models.NullBooleanField()
    gender = models.TextField(null=True)

    # University
    graduationYear = models.IntegerField()
    university = models.TextField()
    degree = models.TextField(default='Computer Science')

    # URLs
    github = models.URLField()
    devpost = models.URLField()
    linkedin = models.URLField()
    site = models.URLField()
    resume = models.URLField()

    # About you
    first_timer = models.NullBooleanField()
    description = models.TextField()
    projects = models.TextField()

    # Info for swag
    diet = models.TextField()
    tshirt_size = models.CharField(max_length=3, default='M')

    # Reimbursement
    scholarship = models.NullBooleanField()
    reimbursement_money = models.IntegerField(blank=True, null=True)

    lennyface = models.TextField(default='-.-')

    # Team
    team = models.NullBooleanField()
    teammates = models.TextField(default='None')

    # Needs to be set to true -> else rejected
    authorized_mlh = models.NullBooleanField()
    status = models.CharField(choices=STATUS, default=APP_STARTED, max_length=2)

    invited_by = models.TextField(null=True)

    # TODO: TEAM EXTERNAL

    def __repr__(self):
        return self.name + ' ' + self.lastname

    def invite(self, request):
        if not request.user.has_perm('register.invite_application'):
            raise ValidationError('User doesn\'t have permission to invite user')
        # We can re-invite someone invited
        if self.status not in [APP_COMPLETED, APP_EXPIRED, APP_INVITED]:
            raise ValidationError('Application needs to be completed to invite. Current status: %s' % self.status)
        if self.status == APP_INVITED:
            self._send_invite(request, mail_title="[HackUPC] Missing answer")
        else:
            self._send_invite(request)
        self.status = APP_INVITED
        self.invitation_date = timezone.now()
        self.last_reminder = None
        self.save()

    def send_last_reminder(self):
        if self.status != APP_INVITED:
            raise ValidationError('Reminder can\'t be sent to non-pending applications')
        self._send_last_reminder()
        self.last_reminder = timezone.now()
        self.save()

    def expire(self):
        self.status = APP_EXPIRED
        self.save()

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
        if self.status == APP_CANCELLED:
            raise ValidationError('This invite has been cancelled.')
        elif self.status == APP_EXPIRED:
            raise ValidationError('Unfortunately your invite has expired.')
        if self.status == APP_INVITED:
            m = MailListManager()
            m.add_applicant_to_list(self, m.W17_GENERAL_LIST_ID)
            self._send_confirmation_ack(cancellation_url)
            self.status = APP_CONFIRMED
            self.save()
        else:
            raise ValidationError('Unfortunately his application hasn\'t been invited [yet]')

    def can_be_cancelled(self):
        return self.status == APP_CONFIRMED or self.status == APP_INVITED

    def cancel(self):
        if not self.can_be_cancelled():
            raise ValidationError('Application can\'t be cancelled. Current status: %s' % self.status)
        if self.status != APP_CANCELLED:
            self.status = APP_CANCELLED
            self.save()
            m = MailListManager()
            m.remove_applicant_from_list(self, m.W17_GENERAL_LIST_ID)

    def confirmation_url(self, request=None):
        return reverse('confirm_app', kwargs={'token': self.id}, request=request)

    def cancelation_url(self, request=None):
        return reverse('cancel_app', kwargs={'token': self.id}, request=request)

    def check_in(self):
        self.status = APP_ATTENDED
        self.save()

    def _send_invite(self, request, mail_title="[HackUPC] You are invited!"):
        sendgrid_send(
            [self.email],
            mail_title,
            {'%name%': self.name,
             '%confirmation_url%': self.confirmation_url(request),
             '%cancellation_url%': self.cancelation_url(request)},
            '513b4761-9c40-4f54-9e76-225c2835b529'
        )

    def _send_last_reminder(self):
        sendgrid_send(
            [self.email],
            "[HackUPC] Invite expires in 24h",
            {'%name%': self.name,
             '%token%': self.id,
             },
            '4295b92e-b71d-4b6d-89ec-a4c5fe75a5f6'

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
            ("invite", "Can invite applications"),
            ("vote", "Can review applications"),
            ("checkin", "Can check-in applications"),
            ("reject", "Can reject applications"),
            ("ranking", "Can view voting ranking"),
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
