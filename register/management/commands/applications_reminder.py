from django.core import mail
from django.core.management.base import BaseCommand

from register import models, emails


class Command(BaseCommand):
    help = 'Sends a reminder to all the hackers that have filled only half of the application'

    def handle(self, *args, **options):
        self.stdout.write('Checking non finished applications...')
        nonfinished_hacker = models.Hacker.objects.filter(application__isnull=True)
        self.stdout.write('Checking non finished applications...%s found' % nonfinished_hacker.count())
        self.stdout.write('Sending reminders...')
        msgs = []
        for hacker in nonfinished_hacker:
            msgs.append(emails.create_applicationreminder(hacker))

        connection = mail.get_connection()
        connection.send_messages(msgs)
        self.stdout.write(self.style.SUCCESS(
            'Sending reminders... Successfully sent %s reminders' % len(msgs)))
