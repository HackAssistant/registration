from django.contrib.auth.mixins import UserPassesTestMixin


class IsOrganizerMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.email_verified:
            return False
        return self.request.user.is_authenticated and self.request.user.is_organizer


class IsVolunteerMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.email_verified:
            return False
        return \
            self.request.user.is_authenticated and (self.request.user.is_volunteer or self.request.user.is_organizer)


class IsDirectorMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.email_verified:
            return False
        return \
            self.request.user.is_authenticated and self.request.user.is_director
