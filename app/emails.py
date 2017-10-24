import json
from logging import error

import sendgrid
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import TemplateDoesNotExist, Context
from django.template.loader import render_to_string
from requests import HTTPError


def sendgrid_send(recipients, subject, substitutions, template_id,
                  from_email='HackUPC Team <contact@hackupc.com>'):
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


def render_mail(template_prefix, recipient_email, substitutions,
                from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Renders an e-mail to `email`.  `template_prefix` identifies the
    e-mail that is to be sent, e.g. "account/email/email_confirmation"
    """

    substitutions.update({
                          'edition_name': settings.CURRENT_EDITION})
    substitutions.update(settings.STATIC_KEYS_TEMPLATES)

    subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                               context=Context(substitutions))
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    prefix = settings.EMAIL_SUBJECT_PREFIX
    if prefix is None:
        prefix = "[{name}] ".format(name='HackUPC')
    subject = prefix + ' ' + subject
    substitutions.update({'subject': subject})

    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}_message.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           Context(substitutions)).strip()
        except TemplateDoesNotExist:
            if ext == 'txt' and not bodies:
                # We need at least one body
                raise
    if 'txt' in bodies:
        msg = EmailMultiAlternatives(subject,
                                     bodies['txt'],
                                     from_email,
                                     [recipient_email])
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(subject,
                           bodies['html'],
                           from_email,
                           [recipient_email])
        msg.content_subtype = 'html'  # Main content is now text/html
    return msg


def send_email(template_prefix, recipient_email, substitutions,
               from_email=settings.DEFAULT_FROM_EMAIL):
    msg = render_mail(template_prefix, recipient_email, substitutions,
                      from_email)
    msg.send()


class MailListManager:
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

    def _create_sendgrid_recipient(self, application):
        recipient = [
            {
                "application_id": application.id,
                "email": application.hacker.user.email,
                "first_name": application.hacker.name,
                "last_name": application.hacker.lastname,
            }
        ]
        response = self.sg.client.contactdb.recipients.post(
            request_body=recipient)
        body = json.loads(response.body.decode('utf-8'))
        if response.status_code != 201 or \
                len(body["persisted_recipients"]) != 1:
            error('Could not create a recipient for the applicant {} ({}). '
                  'SendGrid API responded with status code {}.'
                  .format(application.id, application.name,
                          response.status_code))
        created_id = body["persisted_recipients"][0]
        return created_id

    def _add_recipient_to_list(self, recipient_id, list_id):
        response = self.sg.client.contactdb.lists._(list_id).recipients \
            ._(recipient_id).post()
        if response.status_code != 201:
            error('Could not add recipient {} to list. SendGrid API responded '
                  'with status code {}.'
                  .format(recipient_id, response.status_code))

    def add_applicant_to_list(self, application, list_id):
        # Test if application contains recipientid
        if not application.sendgrid_id:
            # If it doesn't, create recipient on sendgrid and store its id
            recipient_id = self._create_sendgrid_recipient(application)
            application.sendgrid_id = recipient_id
            application.save()

        recipient_id = application.sendgrid_id

        # Add recipient to list
        try:
            self._add_recipient_to_list(recipient_id, list_id)
        except HTTPError:
            pass

    def _remove_recipient_from_list(self, recipient_id, list_id):
        params = {'recipient_id': recipient_id, 'list_id': list_id}
        lists = self.sg.client.contactdb.lists
        try:
            response = lists._(list_id).recipients._(recipient_id).delete(
                query_params=params)

            if response.status_code != 204 and response.status_code != 201:
                error('Could not remove recipient {} from the mail list. '
                      'SendGrid API responded with status code {}.'
                      .format(recipient_id, response.status_code))
        except HTTPError:
            error('Could not remove recipient {} from the mail list. Error '
                  'when calling SendGrid API')

    def remove_applicant_from_list(self, application, list_id):

        if application.sendgrid_id:
            self._remove_recipient_from_list(application.sendgrid_id, list_id)

        else:
            # If it doesn't have a SG id, we still create and save the
            # recipient but there's no need to remove him from anywhere
            recipient_id = self._create_sendgrid_recipient(application)
            application.sendgrid_id = recipient_id
            application.save()
