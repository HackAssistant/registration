from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone


from applications import models, emails


class Command(BaseCommand):
    help = 'Checks invites that have expired and sends reminders 24 before'

    def handle(self, *args, **options):
        fourdaysago = timezone.now() - timedelta(days=4)
        self.stdout.write('Checking reminders...')
        reminders = models.HackerApplication.objects.filter(
            status_update_date__lte=fourdaysago, status=models.APP_INVITED)
        self.stdout.write('Checking reminders...%s found' % reminders.count())
        self.stdout.write('Sending reminders...')
        msgs = []
        for app in reminders:
            app.last_reminder()
            msgs.append(emails.create_lastreminder_email(app))

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))

        onedayago = timezone.now() - timedelta(days=1)
        self.stdout.write('Checking expired...')
        expired = models.HackerApplication.objects.filter(
            status_update_date__lte=onedayago, status=models.APP_LAST_REMIDER)
        self.stdout.write('Checking expired...%s found' % expired.count())
        self.stdout.write('Setting expired...')
        count = len([app.expire() for app in expired])
        self.stdout.write(self.style.SUCCESS(
            'Setting expired... Successfully expired %s applications' % count))
