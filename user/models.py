from __future__ import unicode_literals

import uuid as uuid
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone

USR_ORGANIZER = 'O'
USR_VOLUNTEER = 'V'
USR_HACKER = 'H'
USR_MENTOR = 'M'
USR_SPONSOR = 'S'
USR_HACKER_NAME = 'Hacker'
USR_MENTOR_NAME = 'Mentor'
USR_SPONSOR_NAME = 'Sponsor'
USR_VOLUNTEER_NAME = 'Volunteer'
USR_ORGANIZER_NAME = 'Organizer'

USR_TYPE = [
    (USR_HACKER, USR_HACKER_NAME),
    (USR_MENTOR, USR_MENTOR_NAME),
    (USR_SPONSOR, USR_SPONSOR_NAME),
    (USR_VOLUNTEER, USR_VOLUNTEER_NAME),
    (USR_ORGANIZER, USR_ORGANIZER_NAME),
]

USR_URL_TYPE = {
    USR_HACKER_NAME.lower(): USR_HACKER,
    USR_VOLUNTEER_NAME.lower(): USR_VOLUNTEER,
    USR_MENTOR_NAME.lower(): USR_MENTOR
}

USR_URL_TYPE_CHECKIN = USR_URL_TYPE
USR_URL_TYPE_CHECKIN[USR_SPONSOR_NAME.lower()] = USR_SPONSOR


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, u_type=None):
        if not email:
            raise ValueError('Users must have a email')

        user = self.model(
            email=email,
            name=name,
            type=USR_URL_TYPE[u_type]
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_sponsor(self, email, name, password=None, n_max=1):
        if not email:
            raise ValueError('Users must have a email')

        user = self.model(
            email=email,
            name=name,
            type=USR_SPONSOR,
            max_applications=n_max,
            email_verified=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_mlhuser(self, email, name, mlh_id):
        if not email:
            raise ValueError('Users must have a email')
        if not mlh_id:
            raise ValueError('Users must have a mlh id')

        user = self.model(
            email=email,
            name=name,
            mlh_id=mlh_id
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            name=name,
            password=password,
            u_type='hacker'
        )
        user.type = USR_ORGANIZER
        user.is_director = True
        user.is_admin = True
        user.email_verified = True
        user.is_hardware_admin = True
        user.is_hx = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Full name',
        max_length=255,
    )

    type = models.CharField(choices=USR_TYPE, default=USR_HACKER, max_length=2)

    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_judge = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    can_review_dubious = models.BooleanField(default=False)
    can_review_blacklist = models.BooleanField(default=False)
    is_hardware_admin = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now)
    mlh_id = models.IntegerField(blank=True, null=True, unique=True)
    can_review_volunteers = models.BooleanField(default=False)
    can_review_mentors = models.BooleanField(default=False)
    can_review_sponsors = models.BooleanField(default=False)
    max_applications = models.IntegerField(default=1)
    email_subscribed = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def get_full_name(self):
        # The user is identified by their nickname/full_name address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    @property
    def is_participant(self):
        return not self.is_sponsor and not self.is_mentor and not self.is_judge and not self.is_volunteer and not \
            self.is_organizer

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    @property
    def has_dubious_access(self):
        return self.can_review_dubious or self.is_director

    @property
    def has_blacklist_access(self):
        return self.can_review_blacklist or self.is_director

    @property
    def has_volunteer_access(self):
        return self.can_review_volunteers or self.is_director

    @property
    def has_mentor_access(self):
        return self.can_review_mentors or self.is_director

    @property
    def has_sponsor_access(self):
        return self.can_review_sponsors or self.is_director

    @property
    def is_organizer(self):
        return self.type == USR_ORGANIZER

    def admin_is_organizer(self):
        return self.is_organizer

    admin_is_organizer.boolean = True

    @property
    def is_volunteer_accepted(self):
        if self.type == USR_VOLUNTEER:
            try:
                return self.volunteerapplication_application.is_attended()
            except Exception:
                pass
        return False

    def admin_is_volunteer_accepted(self):
        return self.is_volunteer_accepted

    admin_is_volunteer_accepted.boolean = True

    def have_application(self):
        return self.application is not None

    have_application.boolean = True

    def is_volunteer(self):
        return self.type == USR_VOLUNTEER

    def is_mentor(self):
        return self.type == USR_MENTOR

    def is_sponsor(self):
        return self.type == USR_SPONSOR

    def is_hacker(self):
        return self.type == USR_HACKER

    @property
    def application(self):
        try:
            if self.type == USR_HACKER:
                return self.hackerapplication_application
            if self.type == USR_VOLUNTEER:
                return self.volunteerapplication_application
            if self.type == USR_MENTOR:
                return self.mentorapplication_application
        except Exception:
            return None

    def has_applications_left(self):
        if self.is_sponsor() and self.sponsorapplication_application is not None:
            return len(self.sponsorapplication_application.all()) < self.max_applications
        return False

    @property
    def current_applications(self):
        if self.is_sponsor():
            return len(self.sponsorapplication_application.all())
        return self.application is not None

    def set_mentor(self):
        self.type = USR_MENTOR

    def set_volunteer(self):
        self.type = USR_VOLUNTEER

    @property
    def has_checked_in(self):
        if self.application:
            return self.application.is_attended()
        return False

    @property
    def is_blacklisted(self):
        try:
            user = BlacklistUser.objects.get(email=self.email)
            if user:
                return True
        except BlacklistUser.DoesNotExist:
            return False

    def can_change_type(self):
        if self.have_application():
            return False
        return self.is_hacker() or self.is_mentor() or self.is_volunteer()


class Token(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name='token', primary_key=True, on_delete=models.CASCADE)

    def uuid_str(self):
        return str(self.uuid)


class BlacklistUserManager(models.Manager):
    def create_blacklist_user(self, user, motive_of_ban):
        blacklist_user = self.create(
            email=user.email,
            name=user.name,
            motive_of_ban=motive_of_ban,
            date_of_ban=timezone.now()
        )
        return blacklist_user


class BlacklistUser(models.Model):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Full name',
        max_length=255,
    )

    motive_of_ban = models.CharField(blank=True, max_length=300, null=True)

    date_of_ban = models.DateTimeField()

    objects = BlacklistUserManager()


class LoginRequest(models.Model):
    ip = models.CharField(max_length=30)
    latestRequest = models.DateTimeField()
    login_tries = models.IntegerField(default=1)

    def get_latest_request(self):
        return self.latestRequest

    def set_latest_request(self, latest_request):
        self.latestRequest = latest_request

    def reset_tries(self):
        self.login_tries = 1

    def increment_tries(self):
        self.login_tries += 1
