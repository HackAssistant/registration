from django.db.models.signals import post_save
from django.dispatch import receiver

from applications import models


# Delete DraftApplication when application submitted
@receiver(post_save, sender=models.Application)
def clean_draftapplication(sender, instance, created, *args, **kwargs):
    if not created:
        return None
    # Delete draft as its no longer needed
    models.DraftApplication.objects.filter(user=instance.user).delete()
