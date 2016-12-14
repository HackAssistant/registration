from django.core.mail import EmailMultiAlternatives


def sendgrid_send(recipients, subject, substitutions, template_id):
    from_email = "HackUPC Team <hackers@hackupc.com>"
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
