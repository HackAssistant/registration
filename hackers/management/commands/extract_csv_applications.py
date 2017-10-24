from django.core.management.base import BaseCommand

from register import models

EXPORT_CSV_FIELDS = ['name', 'lastname', 'university', 'country', 'email']


class Command(BaseCommand):
    help = 'Shows applications filtered by state as CSV'

    def add_arguments(self, parser):
        parser.add_argument('-s',
                            dest='state',
                            default=False,
                            help='filter by state')

    def handle(self, *args, **options):
        applications = models.Application.objects.all()

        if options['state']:
            applications = applications.filter(status=options['state'])

        self.stdout.write(','.join(EXPORT_CSV_FIELDS))
        for app in applications:
            res = [app.hacker.name, app.hacker.lastname, app.hacker.university, app.origin_country,
                   app.hacker.user.email]
            self.stdout.write(','.join(res))
