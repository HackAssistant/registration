from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from register.emails import sendgrid_send
from rest_framework.reverse import reverse

status = [
    ('A', 'Accepted'),
    ('P', 'Pending'),
    ('R', 'Rejected'),
    ('I', 'Invited'),
    ('C', 'Confirmed'),
    ('X', 'Cancelled')
]


# Create your models here.

class Application(models.Model):
    id = models.TextField(primary_key=True)

    # Personal data
    name = models.TextField()
    lastname = models.TextField()
    email = models.TextField()
    graduation = models.TextField()
    university = models.TextField()

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
    country = models.TextField()
    schoolarship = models.NullBooleanField()

    # Needs to be set to true -> else rejected
    authorized_mlh = models.NullBooleanField()
    status = models.CharField(choices=status, default='P', max_length=1)

    # TODO: TEAM EXTERNAL

    def invite(self, request):
        if self.status != 'A':
            raise ValidationError('Application needs to be pending to send. Current status: %s' % self.status)
        self._send_invite(request)
        self.status = 'I'
        self.save()

    def confirm(self):
        if self.status != 'I':
            raise ValidationError('Application hasn\'t been invited yet')
        self.status = 'C'
        self.save()

    def cancel(self):
        if self.status != 'C' or self.status != 'I':
            raise ValidationError('Application can\'t be cancelled. Current status: %s' % self.status)
        self.status = 'X'
        self.save()

    def confirmation_url(self, request=None):
        return reverse('confirm_app', kwargs={'token': self.id}, request=request)

    def cancelation_url(self,request=None):
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
