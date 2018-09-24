from __future__ import unicode_literals

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have a email')

        user = self.model(
            email=email,
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.is_director = True
        user.is_organizer = True
        user.is_admin = True
        user.email_verified = True
        user.is_volunteer = True
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
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_volunteer = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now)

    # QR identifier for wristband identification
    qr_identifier = models.CharField(max_length=255, null=True)

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
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
