import re

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from user import tokens, models
from user.models import User

REGEX_PATTERN = getattr(settings, 'REGEX_HACKATHON_ORGANIZER_EMAIL', None)
DEV_EMAILS = getattr(settings, 'HACKATHON_DEV_EMAILS', None)


# Make user organizer or admin if fits regex
@receiver(post_save, sender=User)
def user_organizer(sender, instance, created, *args, **kwargs):
    if not created:
        return None

    if REGEX_PATTERN and re.match(REGEX_PATTERN, instance.email):
        instance.type = models.USR_ORGANIZER
        instance.save()

    if DEV_EMAILS and instance.email in DEV_EMAILS:
        instance.is_admin = True
        instance.save()


# Send user verification
@receiver(post_save, sender=User)
def user_verify_email(sender, instance, created, *args, **kwargs):
    if created and not instance.email_verified:
        msg = tokens.generate_verify_email(instance)
        msg.send()


@receiver(pre_save, sender=User)
def change_type(sender, instance, *args, **kwargs):
    old_user = sender.objects.get(pk=instance.id)
    if old_user and old_user.type != instance.type:
        if old_user.is_volunteer():
            instance.volunteerapplication_application.delete()
        if old_user.is_mentor():
            instance.mentorapplication_application.delete()
        if old_user.is_hacker():
            instance.hackerapplication_application.delete()
        if old_user.is_sponsor():
            instance.sponsorapplication_application.delete()
