from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils import timezone


from applications import models, emails
from applications.views import VIEW_APPLICATION_TYPE


class Command(BaseCommand):
    help = 'Checks invites that have expired and sends reminders 24 before'

    def handle(self, *args, **options):
        fourdaysago = timezone.now() - timedelta(days=4)
        msgs = []
        self.stdout.write('Checking reminders...')
        for Application in VIEW_APPLICATION_TYPE.values():
            reminders = Application.objects.filter(
                status_update_date__lte=fourdaysago, status=models.APP_INVITED)
            self.stdout.write('Checking reminders...%s found' % reminders.count())
            for app in reminders:
                app.last_reminder()
                msgs.append(emails.create_lastreminder_email(app))
        self.stdout.write('Sending reminders...')
        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))

        onedayago = timezone.now() - timedelta(days=1)
        self.stdout.write('Checking expired...')
        for Application in VIEW_APPLICATION_TYPE.values():
            expired = Application.objects.filter(
                status_update_date__lte=onedayago, status=models.APP_LAST_REMIDER)
            self.stdout.write('Checking expired...%s found' % expired.count())
            self.stdout.write('Setting expired...')
            count = len([app.expire() for app in expired])
            self.stdout.write(self.style.SUCCESS(
                'Setting expired... Successfully expired %s applications' % count))
