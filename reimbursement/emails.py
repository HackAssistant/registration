from django.conf import settings

from app import emails
from app.utils import reverse


def create_reimbursement_email(reimb, request):
    hacker = reimb.application.hacker
    c = {
        'hacker': hacker,
        'reimb': reimb,
        'confirm_url': str(reverse('confirm_app', request=request)),
        'form_url': reimb.get_form_url(),
        'cancel_url': str(reverse('cancel_app', request=request))
    }
    if settings.REIMBURSEMENT_EMAIL:
        return emails.render_mail('mails/reimbursement',
                                  hacker.user.email, c,
                                  from_email=settings.REIMBURSEMENT_EMAIL)
    return emails.render_mail('mails/reimbursement',
                              hacker.user.email, c)
