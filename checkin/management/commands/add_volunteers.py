from __future__ import print_function

import csv
import sys

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

EXPORT_CSV_FIELDS = ['username', 'email', 'password', ]

User = get_user_model()


class Command(BaseCommand):
    help = 'Shows applications filtered by state as CSV'

    def add_arguments(self, parser):
        parser.add_argument('-f',
                            dest='csv_filename',
                            default=False,
                            help='csv filename')

    def handle(self, *args, **options):

        with open(options['csv_filename']) as csv_f:
            for row in csv.reader(csv_f):
                username = row[0]
                email = row[1]
                password = row[2]
                try:
                    user = User.objects.filter(email=email).first()

                    if not user:
                        print('Creating user {0}.'.format(email))
                        user = User.objects.create_user(username=username, email=email)
                        user.set_password(password)
                    else:
                        print('Updating permissions for user {0}.'.format(email))

                    checkin_perm = Permission.objects.get(codename='check_in')
                    user.user_permissions.add(checkin_perm)
                    user.save()
                    assert authenticate(username=username, password=password)

                    print('User {0} successfully created.'.format(email))

                except:
                    print('There was a problem creating the user: {0}.  Error: {1}.'
                          .format(email, sys.exc_info()[1]))
