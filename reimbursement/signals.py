from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application
from reimbursement.models import Reimbursement


@receiver(post_save, sender=Application)
def reimbursement_create(sender, instance, created, *args, **kwargs):
    if created and instance.scholarship:
        reimb = Reimbursement()
        reimb.application = instance
        reimb.origin_country = instance.origin_country
        reimb.origin_city = instance.origin_city
        reimb.check_prices()
        reimb.save()
