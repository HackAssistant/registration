from django.core.management.base import BaseCommand

from register import typeform


class Command(BaseCommand):
    help = 'Fetches and updates all forms from Typeform and tries to insert them'

    def handle(self, *args, **options):
        fetched = typeform.FullApplicationsTypeform().insert_forms()
        self.stdout.write(self.style.SUCCESS(
            'Successfully fetched %s forms' % len(fetched)))
