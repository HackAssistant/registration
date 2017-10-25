from app import emails
from app.utils import reverse


def create_reimbursement_email(reimb, request):
    app = reimb.application
    c = {
        'app': app,
        'reimb': reimb,
        'confirm_url': str(reverse('confirm_app', request=request)),
        'form_url': reimb.get_form_url(),
        'cancel_url': str(reverse('cancel_app', request=request))
    }
    return emails.render_mail('mails/reimbursement',
                              app.user.email, c)
