import json
from logging import error

import sendgrid
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from requests import HTTPError


def sendgrid_send(recipients, subject, substitutions, template_id, from_email='HackUPC Team <contact@hackupc.com>'):
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

    def _create_sendgrid_recipient(self, application):
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
            error('Could not create a recipient for the applicant {} ({}). '
                  'SendGrid API responded with status code {}.'
                  .format(application.id, application.name, response.status_code))
        created_id = body["persisted_recipients"][0]
        return created_id

    def _add_recipient_to_list(self, recipient_id, list_id):
        response = self.sg.client.contactdb.lists._(list_id).recipients._(recipient_id).post()
        if response.status_code != 201:
            error('Could not add recipient {} to list. SendGrid API responded with status code {}.'
                  .format(recipient_id, response.status_code))

    def add_applicant_to_list(self, application, list_id):
        # Test if application contains recipientid
        if application.sendgrid_id != "":
            recipient_id = application.sendgrid_id

        else:
            # If it doesn't, create recipient on sendgrid and store its id
            recipient_id = self._create_sendgrid_recipient(application)
            application.sendgrid_id = recipient_id
            application.save()

        # Add recipient to list
        self._add_recipient_to_list(recipient_id, list_id)

    def _remove_recipient_from_list(self, recipient_id, list_id):
        params = {'recipient_id': recipient_id, 'list_id': list_id}
        lists = self.sg.client.contactdb.lists
        try:
            response = lists._(list_id).recipients._(recipient_id).delete(query_params=params)

            if response.status_code != 204 and response.status_code != 201:
                error('Could not remove recipient {} from the mail list. SendGrid API responded with status code {}.'
                      .format(recipient_id, response.status_code))
        except HTTPError:
            error('Could not remove recipient {} from the mail list. Error when calling SendGrid API')

    def remove_applicant_from_list(self, application, list_id):

        if application.sendgrid_id != "":
            recipient_id = application.sendgrid_id
            self._remove_recipient_from_list(recipient_id, list_id)

        else:
            # If it doesn't have a SG id, we still create and save the
            # recipient but there's no need to remove him from anywhere
            recipient_id = self._create_sendgrid_recipient(application)
            application.sendgrid_id = recipient_id
            application.save()
