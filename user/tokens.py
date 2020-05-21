from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from app.utils import reverse as r_reverse
from user.emails import create_verify_email, create_password_reset_email, create_sponsor_link_email
from user.models import Token


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email_verified)
        )


account_activation_token = AccountActivationTokenGenerator()

password_reset_token = PasswordResetTokenGenerator()


def generate_verify_email(user):
    token = account_activation_token.make_token(user)
    uuid = urlsafe_base64_encode(force_bytes(user.pk))
    activate_url = 'http://' + settings.HACKATHON_DOMAIN + \
                   reverse('activate', kwargs={'uid': uuid, 'token': token})
    return create_verify_email(user, activate_url)


def generate_pw_reset_email(user, request):
    token = password_reset_token.make_token(user)
    uuid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = r_reverse('password_reset_confirm', kwargs={'uid': uuid, 'token': token}, request=request)
    return create_password_reset_email(user, reset_url)


def generate_sponsor_link_email(user, request):
    token = password_reset_token.make_token(user)
    t = Token()
    t.user = user
    app_token = t.uuid_str()
    t.save()
    uuid = urlsafe_base64_encode(force_bytes(user.pk))
    user_sponsor_url = r_reverse('password_reset_confirm', kwargs={'uid': uuid, 'token': token}, request=request)
    app_sponsor_url = r_reverse('sponsor_app', kwargs={'uid': uuid, 'token': app_token}, request=request)
    print(user_sponsor_url)
    print(app_sponsor_url)
    return create_sponsor_link_email(request.user, user_sponsor_url, app_sponsor_url, user.name)
