from __future__ import unicode_literals

from django.contrib.auth import models as admin_models
from django.core.exceptions import ValidationError
from django.db import models
from register.emails import sendgrid_send
from rest_framework.reverse import reverse

status = [
    ('A', 'Accepted'),
    ('P', 'Pending'),
    ('R', 'Rejected'),
    ('I', 'Invited'),
    ('C', 'Confirmed'),
    ('X', 'Cancelled'),
    ('T', 'Attended'),
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
    status = models.CharField(choices=status, default='P', max_length=2)

    @property
    def positive_votes(self):
        return self.vote_set.filter(vote=1).count()

    @property
    def negative_votes(self):
        return self.vote_set.filter(vote=-1).count()

    @property
    def votes(self):
        total = self.vote_set.count()
        if not total:
            return total
        return self.positive_votes - (self.negative_votes * 3) / total

    # TODO: TEAM EXTERNAL

    def invite(self, request):
        if not request.user.has_perm('register.invite_application'):
            raise ValidationError('User doesn\'t have permission to invite user')
        if self.status != 'A':
            raise ValidationError('Application needs to be accepted to send. Current status: %s' % self.status)
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

    def cancelation_url(self, request=None):
        return reverse('cancel_app', kwargs={'token': self.id}, request=request)

    def test_url(self,request=None):
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

    # def notify_application(self, subject, reason):
    #     sendgrid_send(
    #         [self.email],
    #         subject,
    #         {'%name%': self.name,
    #          '%reason%': reason,
    #          },
    #         '513b4761-9c40-4f54-9e76-225c2835b529'
    #     )

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     if not self.authorized_mlh:
    #         self.status = 'R'
    #         self.notify_application('Application cancelled',
    #                                 """
    #                                 You haven't accepted MLH Code of conduct.
    #                                  Please apply again and accept it to opt in HackUPC.
    #                                 """)
    #     else:
    #         # self.notify_application('Application received',
    #         #                         """
    #         #                         Thanks for applying to HackUPC. We have received your application.
    #         #                         We can take some time as we review them manually, so please
    #         #                         """)
    #         pass
    #
    #     super(Application, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        permissions = (
            ("accept_application", "Can accept applications"),
            ("invite_application", "Can invite applications"),
            ("attended_application", "Can mark as attended applications"),
            ("reject_application", "Can reject applications"),
            ("force_status", "Can force status application"),
        )


VOTES = (
    ('Positive', 1),
    ('Negative', -1),
    ('Skipped', 0)
)


class Vote(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(admin_models.User)
    vote = models.IntegerField(choices=VOTES)

    class Meta:
        unique_together = ('application', 'user')
