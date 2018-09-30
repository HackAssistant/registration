from __future__ import print_function

import csv
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from app import slack
from app.slack import SlackInvitationException


User = get_user_model()


def slack_invite(self, email):
    try:
        slack.send_slack_invite(email)
        print('Slack invite sent to ' + email + '.')
    except SlackInvitationException as e:
        print('Slack error: ' + str(e))


class Command(BaseCommand):
    """
    Format CSV: email
    """
    help = 'Invites volunteers to Slack'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename',
                            default=False,
                            help='csv filename')

    def handle(self, *args, **options):

        with open(options['csv_filename']) as csv_f:
            for row in csv.reader(csv_f):
                email = row[0]
                try:
                    print('Inviting user {0}.'.format(email))
                    slack_invite(email)

                except:
                    print('There was a problem inviting the user: {0}.  Error: {1}.'
                          .format(email, sys.exc_info()[1]))
