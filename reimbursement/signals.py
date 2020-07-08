from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from applications.models import HackerApplication
from reimbursement.models import Reimbursement, RE_EXPIRED, RE_PEND_TICKET


@receiver(post_save, sender=HackerApplication)
def reimbursement_create(sender, instance, created, *args, **kwargs):
    exists = Reimbursement.objects.filter(hacker=instance.user).exists()
    if not instance.reimb and exists:
        Reimbursement.objects.get(hacker=instance.user).delete()
        return
    if not instance.reimb:
        return
    if exists:
        reimb = Reimbursement.objects.get(hacker=instance.user)
    else:
        reimb = Reimbursement()
    reimb.generate_draft(instance)


@receiver(post_save, sender=Reimbursement)
def reimbursement_unexpire(sender, instance, created, *args, **kwargs):
    if instance.status == RE_EXPIRED and instance.expiration_time and instance.expiration_time > timezone.now():
        instance.status = RE_PEND_TICKET
        instance.save()
