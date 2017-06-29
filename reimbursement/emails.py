from app import emails, settings


def create_reimbursement_email(reimb, request):
    hacker = reimb.application.hacker
    c = {
        'name': hacker.name,
        'form_url': settings.REIMBURSEMENT_APP.get('typeform_form', 'ZrEOYT')
    }
    return emails.render_mail('reimbursement/mails/reimbursement', hacker.user.email, c)
