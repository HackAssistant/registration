from app import emails
from app.utils import reverse


def create_reimbursement_email(reimb, request):
    app = reimb.hacker.application
    c = _get_context(app, reimb, request)
    return emails.render_mail('mails/reimbursement', reimb.hacker.email, c)


def create_reject_receipt_email(reimb, request):
    app = reimb.hacker.application
    c = _get_context(app, reimb, request)
    return emails.render_mail('mails/reject_receipt', reimb.hacker.email, c, from_email=reimb.reimbursed_by.email)


def create_no_reimbursement_email(reimb, request):
    app = reimb.hacker.application
    c = _get_context(app, reimb, request)
    return emails.render_mail('mails/no_reimbursement', reimb.hacker.email, c)


def _get_context(app, reimb, request):
    return {
        'app': app,
        'reimb': reimb,
        'confirm_url': str(reverse('confirm_app', kwargs={'id': app.uuid_str}, request=request)),
        'form_url': str(reverse('reimbursement_dashboard', request=request)),
        'cancel_url': str(reverse('cancel_app', kwargs={'id': app.uuid_str}, request=request))
    }
