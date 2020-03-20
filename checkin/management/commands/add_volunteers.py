from __future__ import print_function

import csv
import sys

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from user import models

User = get_user_model()


class Command(BaseCommand):
    """
    Format CSV: name,email,password
    """
    help = 'Creates volunteers accounts'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename',
                            default=False,
                            help='csv filename')

    def handle(self, *args, **options):

        with open(options['csv_filename']) as csv_f:
            for row in csv.reader(csv_f):
                name = row[0]
                email = row[1]
                password = row[2]
                try:
                    user = User.objects.filter(email=email).first()

                    if not user:
                        print('Creating user {0}.'.format(email))
                        user = User.objects.create_user(name=name, email=email)
                        user.set_password(password)
                    else:
                        print('Updating permissions for user {0}.'.format(email))
                    user.type = models.USR_VOLUNTEER
                    user.save()
                    assert authenticate(email=email, password=password)

                    print('User {0} successfully created.'.format(email))

                except:
                    print('There was a problem creating the user: {0}.  Error: {1}.'
                          .format(email, sys.exc_info()[1]))
