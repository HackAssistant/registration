from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class IsHackerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        return self.request.user.is_authenticated


class IsOrganizerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        return self.request.user.is_authenticated and self.request.user.is_organizer


class IsSponsorMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        return self.request.user.is_authenticated and self.request.user.is_sponsor()


class IsVolunteerMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        return \
            self.request.user.is_authenticated and \
            (self.request.user.is_volunteer_accepted or self.request.user.is_organizer)


class IsDirectorMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
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
        if not self.request.user.has_usable_password():
            return False
        return self.request.user.is_hardware_admin or self.request.user.is_organizer


class HaveDubiousPermissionMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        if not self.request.user.is_organizer:
            return False
        return self.request.user.has_dubious_access


class HaveVolunteerPermissionMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        if not self.request.user.is_organizer:
            return False
        return self.request.user.has_volunteer_access


class HaveMentorPermissionMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        if not self.request.user.is_organizer:
            return False
        return self.request.user.has_mentor_access


class HaveSponsorPermissionMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        if not self.request.user.is_organizer:
            return False
        return self.request.user.has_sponsor_access


class IsBlacklistAdminMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        return self.request.user.has_blacklist_acces or self.request.user.is_director


class DashboardMixin(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.email_verified:
            return False
        if not self.request.user.has_usable_password():
            return False
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_hacker() or self.request.user.is_volunteer() or self.request.user.is_mentor()


def is_organizer(f, raise_exception=True):
    """
    Decorator for views that checks whether a user is an organizer or not
    """

    def check_perms(user):
        if user.is_authenticated and user.email_verified and user.is_organizer and user.has_usable_password():
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False

    return user_passes_test(check_perms)(f)


def is_hacker(f, raise_exception=True):
    """
    Decorator for views that checks whether a user is a hacker or not
    """

    def check_perms(user):
        if user.is_authenticated and user.email_verified and user.has_usable_password():
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False

    return user_passes_test(check_perms)(f)
