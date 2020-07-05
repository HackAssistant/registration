from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import model_to_dict

from applications import models


# Delete DraftApplication when application submitted
@receiver(post_save, sender=models.HackerApplication)
@receiver(post_save, sender=models.MentorApplication)
@receiver(post_save, sender=models.VolunteerApplication)
def clean_draft_application(sender, instance, created, *args, **kwargs):
    print('borrar')
    if not created:
        return None
    # Delete draft as its no longer needed
    models.DraftApplication.objects.filter(user=instance.user).delete()


# Create DraftApplication when application deleted
@receiver(post_delete, sender=models.HackerApplication)
@receiver(post_delete, sender=models.MentorApplication)
@receiver(post_delete, sender=models.VolunteerApplication)
def create_draft_application(sender, instance, *args, **kwargs):
    print('crear')
    dict = model_to_dict(instance)
    for key in ['user', 'invited_by', 'submission_date', 'status_update_date', 'status', 'resume']:
        dict.pop(key, None)
    d = models.DraftApplication()
    d.user = instance.user
    d.save_dict(dict)
    d.save()
