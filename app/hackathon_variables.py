# -*- coding: utf-8 -*-
# HACKATHON PERSONALIZATION
import os

from django.utils import timezone

HACKATHON_NAME = 'HackUPC'
# What's the name for the application
HACKATHON_APPLICATION_NAME = 'My HackUPC'
# Hackathon timezone
TIME_ZONE = 'CET'
# This description will be used on the html and sharing meta tags
HACKATHON_DESCRIPTION = 'Join us for BarcelonaTech\'s hackathon. 700 hackers. 36h. October 19th-21st.'
# Domain where application is deployed, can be set by env variable
HACKATHON_DOMAIN = os.environ.get('DOMAIN', 'localhost:8000')
# Hackathon contact email: where should all hackers contact you. It will also be used as a sender for all emails
HACKATHON_CONTACT_EMAIL = 'contact@hackupc.com'
# Hackathon logo url, will be used on all emails
HACKATHON_LOGO_URL = 'https://my.hackupc.com/static/logo.png'

HACKATHON_OG_IMAGE = 'https://hackupc.com/assets/img/hackupc-ogimage@2x.png?v=2018'
# (OPTIONAL) Track visits on your website
HACKATHON_GOOGLE_ANALYTICS = 'UA-69542332-2'
# (OPTIONAL) Hackathon Twitter user
HACKATHON_TWITTER_ACCOUNT = 'hackupc'
# (OPTIONAL) Hackathon Facebook page
HACKATHON_FACEBOOK_PAGE = 'hackupc'
# (OPTIONAL) Hackathon YouTube channel
HACKATHON_YOUTUBE_PAGE = 'UCiiRorGg59Xd5Sjj9bjIt-g'
# (OPTIONAL) Hackathon Instagram user
HACKATHON_INSTAGRAM_ACCOUNT = 'hackupc'
# (OPTIONAL) Hackathon Medium user
HACKATHON_MEDIUM_ACCOUNT = 'hackupc'
# (OPTIONAL) Github Repo for this project (so meta)
HACKATHON_GITHUB_REPO = 'https://github.com/hackupc/registration/'

# (OPTIONAL) Applications deadline
# HACKATHON_APP_DEADLINE = timezone.datetime(2018, 2, 24, 3, 14, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) When to arrive at the hackathon
HACKATHON_ARRIVE = 'Registration opens at 3:00PM and closes at 6:00PM on Friday October 5th, ' \
                   'the opening ceremony will be at 7:00PM.'

# (OPTIONAL) When to arrive at the hackathon
HACKATHON_LEAVE = 'Closing ceremony will be held on Sunday October 7th from 3:00PM to 5:00PM. ' \
                  'However the projects demo fair will be held in the morning from 10:30AM to 1:00PM.'
# (OPTIONAL) Hackathon live page
HACKATHON_LIVE_PAGE = 'https://hackupc.com/live'

# (OPTIONAL) Regex to automatically match organizers emails and set them as organizers when signing up
REGEX_HACKATHON_ORGANIZER_EMAIL = '^.*@hackupc\.com$'

# (OPTIONAL) Send 500 errors to email while on production mode
HACKATHON_DEV_EMAILS = ['devs@hackupc.com', ]

# Reimbursement configuration
REIMBURSEMENT_ENABLED = True
DEFAULT_REIMBURSEMENT_AMOUNT = 100
CURRENCY = '€'
REIMBURSEMENT_EXPIRY_DAYS = 5
REIMBURSEMENT_REQUIREMENTS = 'You have to submit a project and demo it during the event in order to get reimbursed'
REIMBURSEMENT_DEADLINE = timezone.datetime(2018, 2, 24, 3, 14, tzinfo=timezone.pytz.timezone(TIME_ZONE))

# (OPTIONAL) Max team members. Defaults to 4
TEAMS_ENABLED = True
HACKATHON_MAX_TEAMMATES = 4

# (OPTIONAL) Slack credentials
# Highly recommended to create a separate user account to extract the token from
SLACK = {
    'team': os.environ.get('SL_TEAM', 'test'),
    # Get it here: https://api.slack.com/custom-integrations/legacy-tokens
    'token': os.environ.get('SL_TOKEN', None)
}

# (OPTIONAL) Logged in cookie
# This allows to store an extra cookie in the browser to be shared with other application on the same domain
# LOGGED_IN_COOKIE_DOMAIN = '.gerard.space'
# LOGGED_IN_COOKIE_KEY = 'hackassistant_logged_in'
