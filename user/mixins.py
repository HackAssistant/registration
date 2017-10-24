from django.contrib.auth.mixins import UserPassesTestMixin


class IsOrganizerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_organizer


class IsVolunteerMixin(UserPassesTestMixin):
    def test_func(self):
        return \
            self.request.user.is_authenticated and (self.request.user.is_volunteer or self.request.user.is_organizer)
