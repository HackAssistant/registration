from urllib.error import HTTPError

from django.core.management.base import BaseCommand
import json

from register.models import Application
from register.emails import MailListManager
from django.conf import settings
import sendgrid


class Command(BaseCommand):
    help = 'Adds new hackers with reimbursement money to the SendGrid TR mail list'

    def handle(self, *args, **options):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        internationals = Application.objects.filter(reimbursement_money__gt=0)
        internationals_ids = [a.sendgrid_id for a in internationals if a.sendgrid_id]

        m = MailListManager()
        list_id = m.W17_TRAVEL_REIMB_LIST_ID
        params = {'page': 1, 'page_size': 1000}

        try:
            # Fecth recipients that already belong to the mail list
            response = sg.client.contactdb.lists._(list_id).recipients.get(query_params=params)
            existent_recipients = json.loads(response.body.decode('utf-8'))['recipients']
            existent_recipients_id = [r['id'] for r in existent_recipients]

            new_recipients = [sg_id for sg_id in internationals_ids if sg_id not in existent_recipients_id]
            if new_recipients:
                # Add the new recipients to the mail list
                response = sg.client.contactdb.lists._(list_id).recipients.post(request_body=new_recipients)
                if response.status_code == 201:
                    self.stdout.write(self.style.SUCCESS(
                        'Successfully added %d hackers to the SendGrid list' % len(new_recipients)))
            else:
                self.stdout.write(self.style.WARNING('No new recipients to add to the list found'))
        except HTTPError as e:
            self.stdout.write(self.style.ERROR('HTTPError when '))
            self.stdout.write(self.style.ERROR(str(e.code) + " " + e.msg))
            raise e
