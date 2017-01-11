import json

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import sendgrid


def sendgrid_send(recipients, subject, substitutions, template_id):
    from_email = "HackUPC Team <contact@hackupc.com>"
    mail = EmailMultiAlternatives(
        subject=subject,
        body='-',
        from_email=from_email,
        to=recipients,
    )
    # Add template
    mail.attach_alternative(
        "<p>Invite email to HackUPC</p>", "text/html"
    )
    mail.template_id = template_id
    # Replace substitutions in sendgrid template
    mail.substitutions = substitutions
    mail.send()


class MailListManager:
    WINTER_17_LIST_ID = "876178"

    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

    def _add_recipient_to_list(self, recipient_id, list_id):
        response = self.sg.client.contactdb.lists._(list_id).recipients._(recipient_id).post()
        if response.status_code != 201:
            raise ConnectionError  # TODO: raise an appropriate exception/error

    def add_applicant_to_list(self, application, list_id):
        # Test if application contains recipientid
        if application.sendgrid_id != "":
            recipient_id = application.sendgrid_id

        else:
            # If it doesn't, create recipient on sendgrid and store its id
            recipient = [
                {
                    "application_id": application.id,
                    "email": application.email,
                    "first_name": application.name,
                    "last_name": application.lastname,
                }
            ]
            response = self.sg.client.contactdb.recipients.post(request_body=recipient)
            body = json.loads(response.body.decode('utf-8'))

            if response.status_code != 201 or len(body["persisted_recipients"]) != 1:
                raise ConnectionError # TODO: raise an appropriate exception/error

            recipient_id = body["persisted_recipients"][0]
            application.sendgrid_id = recipient_id
            application.save()

        # Add recipient to list
        self._add_recipient_to_list(recipient_id, list_id)

    def remove_recipient_from_list(self, recipient_id, list_id):
        params = {'recipient_id': recipient_id, 'list_id': list_id}
        lists = self.sg.client.contactdb.lists
        response = lists._(list_id).recipients._(recipient_id).delete(query_params=params)

        if response.status_code != 201:
            raise ConnectionError