from django.core.management.base import BaseCommand

from applications.models import SponsorApplication
from user.models import User, USR_ORGANIZER


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email='organizer@organizer.com').exists():
            User.objects.create_sponsor(email='organizer@organizer.com', name='Organizers')
        i = 0
        organizers = User.objects.filter(type=USR_ORGANIZER)
        for organizer in organizers:
            while User.objects.filter(email='organizer+%s@organizer.com' % i).exists():
                i += 1
            user = User.objects.create_sponsor(email='organizer+%s@organizer.com' % i, name=organizer.name)
            SponsorApplication(name=organizer.name, user=user).save()
            i += 1
