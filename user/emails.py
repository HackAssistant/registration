from app import emails


def create_verify_email(user, activate_url):
    c = {
        'user': user,
        'activate_url': activate_url
    }
    return emails.render_mail('mails/verify_email',
                              user.email, c)


def create_password_reset_email(user, reset_url):
    c = {
        'user': user,
        'reset_url': reset_url
    }
    return emails.render_mail('mails/password_reset',
                              user.email, c)
