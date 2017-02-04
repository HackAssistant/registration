from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.datetime_safe import datetime
from register import models


class Command(BaseCommand):
    help = 'Checks invites that have expired and sends reminders 24 before'

    def handle(self, *args, **options):
        fourdaysago = datetime.today() - timedelta(days=4)
        self.stdout.write('Checking reminders...')
        reminders = models.Application.objects.filter(invitation_date__lte=fourdaysago, status=models.APP_INVITED,
                                                      last_reminder=None)
        self.stdout.write('Checking reminders...%s found' % reminders.count())
        self.stdout.write('Sending reminders...')

        count_reminder = len([app.send_last_reminder() for app in reminders])
        self.stdout.write(self.style.SUCCESS('Sending reminders...Successfully sent %s reminders' % count_reminder))

        onedayago = datetime.today() - timedelta(days=1)
        self.stdout.write('Checking expired...')
        expired = models.Application.objects.filter(last_reminder__lte=onedayago, status=models.APP_INVITED)
        self.stdout.write('Checking expired...%s found' % expired.count())
        self.stdout.write('Setting expired...')

        count_reminder = len([app.send_last_reminder() for app in reminders])
        self.stdout.write(self.style.SUCCESS('Setting reminders...Successfully sent %s reminders' % count_reminder))
