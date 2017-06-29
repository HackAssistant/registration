import re

from allauth.account.signals import user_signed_up
from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(user_signed_up)
def organizer_account(request, user, *args, **kwargs):
    pattern = settings.STATIC_KEYS_TEMPLATES.get('r_organizer_email', None)
    if not pattern:
        return None
    if re.match(pattern, user.email):
        vote_perm = Permission.objects.get(codename='vote')
        rank_perm = Permission.objects.get(codename='ranking')
        user.user_permissions.add(vote_perm, rank_perm)
        user.save()


@receiver(post_migrate)
def default_site(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    try:
        Site = apps.get_model('sites', 'Site')
    except LookupError:
        return

    Site(pk=getattr(settings, 'SITE_ID', 1), domain=getattr(settings, 'EVENT_DOMAIN', "example.com"),
         name=getattr(settings, 'EVENT_NAME', "example.com")) \
        .save()
    # We set an explicit pk instead of relying on auto-incrementation,
    # so we need to reset the database sequence. See #17415.
    sequence_sql = connections[using].ops.sequence_reset_sql(no_style(), [Site])
    if sequence_sql:
        if verbosity >= 2:
            print("Resetting sequence")
        with connections[using].cursor() as cursor:
            for command in sequence_sql:
                cursor.execute(command)
