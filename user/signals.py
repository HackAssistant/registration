import re

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from user import tokens
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


# Send user verification
@receiver(post_save, sender=User)
def user_verify_email(sender, instance, created, *args, **kwargs):
    if created and not instance.email_verified:
        msg = tokens.generate_verify_email(instance)
        msg.send()
