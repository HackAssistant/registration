from __future__ import unicode_literals

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

USR_URL_SPONSOR = USR_SPONSOR_NAME.lower()
USR_URL_TYPE = {
    USR_HACKER_NAME.lower(): USR_HACKER,
    USR_VOLUNTEER_NAME.lower(): USR_VOLUNTEER,
    USR_MENTOR_NAME.lower(): USR_MENTOR,
    USR_URL_SPONSOR: USR_SPONSOR
}


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
        user.is_director = True
        user.is_organizer = True
        user.is_admin = True
        user.email_verified = True
        user.is_volunteer = True
        user.is_hardware_admin = True
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
    is_director = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    can_review_dubious = models.BooleanField(default=False)
    is_hardware_admin = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now)
    mlh_id = models.IntegerField(blank=True, null=True, unique=True)

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
    def has_dubious_acces(self):
        return self.can_review_dubious or self.is_director

    @property
    def check_is_organizer(self):
        return self.type == USR_ORGANIZER

    @property
    def check_is_volunteer(self):
        return self.type == USR_VOLUNTEER
