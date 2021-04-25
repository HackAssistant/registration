import os

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from applications import models


@receiver(post_save, sender=models.HackerApplication)
@receiver(post_save, sender=models.MentorApplication)
@receiver(post_save, sender=models.VolunteerApplication)
def clean_draft_application(sender, instance, created, *args, **kwargs):
    if not created:
        return None
    # Delete draft as its no longer needed
    models.DraftApplication.objects.filter(user=instance.user).delete()


# Delete resume file when application deleted
@receiver(post_delete, sender=models.HackerApplication)
@receiver(post_delete, sender=models.MentorApplication)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.resume:
        if os.path.isfile(instance.resume.path):
            os.remove(instance.resume.path)


# Delete resume file when resume changed
@receiver(pre_save, sender=models.HackerApplication)
@receiver(pre_save, sender=models.MentorApplication)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_resume = sender.objects.get(pk=instance.pk).resume
    except sender.DoesNotExist:
        return False
    if old_resume:
        new_resume = instance.resume
        if not old_resume == new_resume:
            if os.path.isfile(old_resume.path):
                os.remove(old_resume.path)
