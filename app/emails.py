from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import TemplateDoesNotExist, Context
from django.template.loader import render_to_string


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
