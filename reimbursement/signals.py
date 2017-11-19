from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application
from reimbursement.models import Reimbursement


@receiver(post_save, sender=Application)
def reimbursement_create(sender, instance, created, *args, **kwargs):
    if instance.scholarship:
        reimb = Reimbursement.objects.get_or_create(hacker=instance.user)
        reimb.generate_draft(instance)
    else:
        reimb = Reimbursement.objects.filter(hacker=instance.user).delete()
