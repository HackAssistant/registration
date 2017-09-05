from datetime import timedelta

from django.core import mail
from django.core.management.base import BaseCommand
from django.utils.datetime_safe import datetime

from register import models, emails


class Command(BaseCommand):
    help = 'Sends a reminder to all the hackers that have filled only half of the application ' \
           'and have registered more than 4 days ago'

    def handle(self, *args, **options):
        self.stdout.write('Checking non finished applications...')
        fourdaysago = datetime.today() - timedelta(days=4)
        nonfinished_hacker = models.Hacker.objects.filter(application__isnull=True, user__date_joined__lte=fourdaysago,
                                                          reminders_sent__exact=0)
        self.stdout.write('Checking non finished applications...%s found' % nonfinished_hacker.count())
        self.stdout.write('Sending reminders...')
        msgs = []
        for hacker in nonfinished_hacker:
            hacker.send_reminder()
            msgs.append(emails.create_applicationreminder(hacker))

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))
