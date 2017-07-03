from django.conf import settings

from app import emails
from app.utils import reverse


def create_invite_email(application, request):
    c = {
        'name': application.hacker.name,
        'reimbursement': application.scholarship,
        'confirm_url': str(reverse('confirm_app', request=request)),
        'cancel_url': str(reverse('cancel_app', request=request))
    }
    return emails.render_mail('register/mails/invitation', application.hacker.user.email, c)


def create_confirmation_email(application, request):
    c = {
        'name': application.hacker.name,
        'token': application.id,
        'qr_url': 'http://chart.googleapis.com/chart?cht=qr&chs=350x350&chl=%s' % application.id,
        'cancel_url': str(reverse('cancel_app', request=request)),
    }
    return emails.render_mail('register/mails/confirmation', application.hacker.user.email, c)


def create_lastreminder_email(application):
    c = {
        'name': application.hacker.name,
        # We need to make sure to redirect HTTP to HTTPS in production
        'confirm_url': 'http://%s%s' % (settings.EVENT_DOMAIN, reverse('confirm_app')),
        'cancel_url': 'http://%s%s' % (settings.EVENT_DOMAIN, reverse('cancel_app')),
    }
    return emails.render_mail('register/mails/last_reminder', application.hacker.user.email, c)
