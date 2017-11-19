from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application
from reimbursement.models import Reimbursement


@receiver(post_save, sender=Application)
def reimbursement_create(sender, instance, created, *args, **kwargs):
    exists = Reimbursement.objects.filter(hacker=instance.user).exists()
    if not instance.reimb:
        Reimbursement.objects.get(hacker=instance.user).delete()
        return
    if exists:
        reimb = Reimbursement.objects.get(hacker=instance.user)
    else:
        reimb = Reimbursement()
    reimb.generate_draft(instance)
