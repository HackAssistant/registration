from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class IsOrganizerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        return self.request.user.is_authenticated and self.request.user.is_organizer


class IsVolunteerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        return \
            self.request.user.is_authenticated and (self.request.user.is_volunteer or self.request.user.is_organizer)


class IsExternalMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        return \
            self.request.user.is_authenticated and (self.request.user.is_external or self.request.user.is_organizer)


class IsDirectorMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        return \
            self.request.user.is_authenticated and self.request.user.is_director


class IsHardwareAdminMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        return self.request.user.is_hardware_admin or self.request.user.is_organizer


def is_organizer(f, raise_exception=True):
    """
    Decorator for views that checks whether a user is an organizer or not
    """

    def check_perms(user):
        if user.is_authenticated and user.email_verified and user.is_organizer:
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False

    return user_passes_test(check_perms)(f)
