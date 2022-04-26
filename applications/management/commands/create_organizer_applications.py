from django.core.management.base import BaseCommand

from applications.models import SponsorApplication
from user.models import User, USR_ORGANIZER


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create_sponsor(email='organizer@organizer.com', name='Organizers')
        organizers = User.objects.filter(type=USR_ORGANIZER)
        for organizer in organizers:
            SponsorApplication(name=organizer.name, user=user).save()
