from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import TemplateDoesNotExist, Context
from django.template.loader import render_to_string

from app import utils

FROM_EMAIL = settings.HACKATHON_NAME + ' Team <' + settings.HACKATHON_CONTACT_EMAIL + '>'


def render_mail(template_prefix, recipient_email, substitutions,
                from_email=FROM_EMAIL, action_required=False):
    """
    Renders an e-mail to `email`.  `template_prefix` identifies the
    e-mail that is to be sent, e.g. "account/email/email_confirmation"
    """
    substitutions.update(utils.get_substitutions_templates())
    subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                               context=substitutions)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    prefix = '[' + settings.HACKATHON_NAME + ']'
    if action_required:
        prefix = '[ACTION REQUIRED]'
    subject = prefix + ' ' + subject
    substitutions.update({'subject': subject})

    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}_message.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           substitutions).strip()
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
               from_email=FROM_EMAIL):
    msg = render_mail(template_prefix, recipient_email, substitutions,
                      from_email)
    msg.send()
