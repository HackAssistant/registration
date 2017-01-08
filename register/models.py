from __future__ import unicode_literals

from django.contrib.auth import models as admin_models
from django.core.exceptions import ValidationError
from django.db import models
from register.emails import sendgrid_send
from register.utils import reverse

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

class Application(models.Model):
    id = models.TextField(primary_key=True)
    submission_date = models.DateTimeField()

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

    @property
    def votes(self):
        total = self.vote_set.count()
        if not total:
            return total
        positive = self.vote_set.filter(vote=1).count()
        negative = self.vote_set.filter(vote=-1).count()
        return positive - (negative * 3) / total

    # TODO: TEAM EXTERNAL

    def invite(self, request):
        if not request.user.has_perm('register.invite_application'):
            raise ValidationError('User doesn\'t have permission to invite user')
        if self.status != APP_ACCEPTED:
            raise ValidationError('Application needs to be accepted to send. Current status: %s' % self.status)
        self._send_invite(request)
        self.status = APP_INVITED
        self.save()

    def is_confirmed(self):
        return self.status == APP_CONFIRMED

    def confirm(self, cancellation_url):
        if self.status != APP_INVITED and self.status != APP_CONFIRMED:
            raise ValidationError('Application hasn\'t been invited yet')
        if self.status != APP_CONFIRMED:
            self._send_confirmation_ack(cancellation_url)
            self.status = APP_CONFIRMED
            self.save()

    def can_be_cancelled(self):
        return self.status == APP_CONFIRMED or self.status == APP_INVITED

    def cancel(self):
        if not self.can_be_cancelled():
            raise ValidationError('Application can\'t be cancelled. Current status: %s' % self.status)
        self.status = APP_CANCELLED
        self.save()

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

    def _send_confirmation_ack(self, cancellation_url):
        sendgrid_send(
            [self.email],
            "[HackUPC] You confirmed your attendance!",
            {'%name%': self.name,
             '%cancellation_url%': cancellation_url},
            'c4d4d758-974f-437b-af9a-d8532f96d670'
        )

    class Meta:
        permissions = (
            ("accept_application", "Can accept applications"),
            ("invite_application", "Can invite applications"),
            ("attended_application", "Can mark as attended applications"),
            ("reject_application", "Can reject applications"),
            ("force_status", "Can force status application"),
        )

VOTE_POSITIVE = 1
VOTE_NEGATIVE = -1
VOTE_SKIP = 0
VOTES = (
    (VOTE_POSITIVE, 'Positive'),
    (VOTE_NEGATIVE, 'Negative'),
    (VOTE_SKIP, 'Skipped'),
)


class Vote(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(admin_models.User)
    vote = models.IntegerField(choices=VOTES)

    class Meta:
        unique_together = ('application', 'user')
