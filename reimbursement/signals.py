from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application
from reimbursement.models import Reimbursement


@receiver(post_save, sender=Application)
def reimbursement_create(sender, instance, created, *args, **kwargs):
    if created and instance.scholarship:
        reimb = Reimbursement()
        reimb.generate_draft(instance)
