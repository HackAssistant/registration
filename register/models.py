from __future__ import unicode_literals

from django.db import models

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
    first_timer = models.BooleanField()
    description = models.TextField()
    projects = models.TextField()
    diet = models.TextField()
    country = models.TextField()
    schoolarship = models.BooleanField()

    # Needs to be set to true -> else rejected
    authorized_mlh = models.BooleanField()
    status = models.CharField(choices=status, default='P')

    # TODO: TEAM

    def invite(self):
        if self.status != 'A':
            raise ValueError('You can\'t invite a non accepted application')
        self.status = 'I'

    def confirm(self):
        if self.status != 'I':
            raise ValueError('Application hasn\'t been invited yet')
        self.status = 'C'

    def cancel(self):
        self.status = 'X'

    @property
    def confirmation_url(self):
        return ''

    @property
    def cancelation_url(self):
        return ''
