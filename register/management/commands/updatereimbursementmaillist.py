from django.core.management.base import BaseCommand
from register.models import Application
from register.emails import MailListManager


class Command(BaseCommand):
    help = 'Fetches last forms from Typeform'

    def handle(self, *args, **options):
        m = MailListManager()
        internationals_with_reimb = Application.objects.exclude(
            reimbursement_money__isnull=False, reimbursement_money__gt=0)

        for appl in internationals_with_reimb:
            m.add_applicant_to_list(appl, m.W17_TRAVEL_REIMB_LIST_ID)

        print(len(internationals_with_reimb))
        self.stdout.write(self.style.SUCCESS('Found %s hackers with allotted reimbursement' % len(internationals_with_reimb)))
