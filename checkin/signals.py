import re

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import Permission
from django.dispatch import receiver


@receiver(user_signed_up)
def organizer_account(request, user, *args, **kwargs):
    pattern = settings.STATIC_KEYS_TEMPLATES.get('r_organizer_email', None)
    if not pattern:
        return None
    if re.match(pattern, user.email):
        checkin_perm = Permission.objects.get(codename='checkin')
        user.user_permissions.add(checkin_perm)
        user.save()
