from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Permission
from allauth.account.models import EmailAddress
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
import getpass
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Please sign up at /accounts/signup using any @hackupc.com email")



