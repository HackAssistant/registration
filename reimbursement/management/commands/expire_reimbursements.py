from django.core.management.base import BaseCommand
from django.utils import timezone


from reimbursement import models


class Command(BaseCommand):
    help = 'Checks reimbursements that have expired'

    def handle(self, *args, **options):
        self.stdout.write('Checking expired reimbursements...')
        reimbs = models.Reimbursement.objects.filter(
            expiration_time__lte=timezone.now(), status=models.RE_PEND_TICKET)
        self.stdout.write('Checking expired reimbursements...%s found' % reimbs.count())
        for reimb in reimbs:
            reimb.expire()

