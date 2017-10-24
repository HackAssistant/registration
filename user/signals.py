import re

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User

REGEX_PATTERN = getattr(settings, 'REGEX_HACKATHON_ORGANIZER_EMAIL', None)

# MAke user organizer if fits regex
@receiver(post_save, sender=User)
def user_organizer(sender, instance, created, *args, **kwargs):
    if not REGEX_PATTERN or not created:
        return None
    if re.match(REGEX_PATTERN, instance.email):
        instance.is_organizer = True
        instance.save()
