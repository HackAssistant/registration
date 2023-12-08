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
HACKATHON_DESCRIPTION = 'Join us for BarcelonaTech\'s hackathon. 36h. May 12 - 14.'
# Domain where application is deployed, can be set by env variable
HACKATHON_DOMAIN = os.environ.get('DOMAIN', None)
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
if HEROKU_APP_NAME and not HACKATHON_DOMAIN:
    HACKATHON_DOMAIN = '%s.herokuapp.com' % HEROKU_APP_NAME
elif not HACKATHON_DOMAIN:
    HACKATHON_DOMAIN = 'localhost:8000'
# Hackathon contact email: where should all hackers contact you. It will also be used as a sender for all emails
HACKATHON_CONTACT_EMAIL = 'contact@hackupc.com'
# Hackathon logo url, will be used on all emails
HACKATHON_LOGO_URL = 'https://my.hackupc.com/static/logo.png'

HACKATHON_OG_IMAGE = 'https://hackupc.com/ogimage.png?v=2021'
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
HACKATHON_GITHUB_REPO = 'https://github.com/hackupc/myhackupc/'

# (OPTIONAL) Applications deadline
HACKATHON_APP_DEADLINE = timezone.datetime(2024, 5, 3, 23, 59, tzinfo=timezone.pytz.timezone(TIME_ZONE))
VOLUNTEER_APP_DEADLINE = timezone.datetime(2024, 5, 9, 23, 59, tzinfo=timezone.pytz.timezone(TIME_ZONE))
MENTOR_APP_DEADLINE = timezone.datetime(2024, 5, 1, 23, 59, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) Online checkin activated
ONLINE_CHECKIN = timezone.datetime(2022, 4, 29, 17, 00, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) When to arrive at the hackathon
HACKATHON_ARRIVE = ''

# (OPTIONAL) When to arrive at the hackathon
HACKATHON_LEAVE = ''

# (OPTIONAL) Hackathon live page
HACKATHON_LIVE_PAGE = 'https://live.hackupc.com'

# (OPTIONAL) Regex to automatically match organizers emails and set them as organizers when signing up
REGEX_HACKATHON_ORGANIZER_EMAIL = '^.*@hackupc\.com$'

# (OPTIONAL) Send 500 errors to email while on production mode
HACKATHON_DEV_EMAILS = ['devs@hackupc.com', ]

# Baggage configuration
BAGGAGE_ENABLED = True
BAGGAGE_PICTURE = True

# Reimbursement configuration
REIMBURSEMENT_ENABLED = True
DEFAULT_REIMBURSEMENT_AMOUNT = 100
CURRENCY = '€'
REIMBURSEMENT_EXPIRY_DAYS = 5
REIMBURSEMENT_REQUIREMENTS = 'You have to submit a project and demo it during the event in order to get reimbursed'
REIMBURSEMENT_DEADLINE = timezone.datetime(2023, 5, 11, 23, 59, tzinfo=timezone.pytz.timezone(TIME_ZONE))

# (OPTIONAL) Max team members. Defaults to 4
TEAMS_ENABLED = True
HACKATHON_MAX_TEAMMATES = 4

# (OPTIONAL) Code of conduct link
# CODE_CONDUCT_LINK = "https://pages.hackcu.org/code_conduct/"

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

# Hardware configuration
# Hardware request time length (in minutes)
HARDWARE_ENABLED = True
#Hardware request time length (in minutes)
HARDWARE_REQUEST_TIME = 15


SLACK_BOT = {
    'id': os.environ.get('SL_BOT_ID', None),
    'token': os.environ.get('SL_BOT_TOKEN', None),
    'channel': os.environ.get('SL_BOT_CHANNEL', None),
    'director1': os.environ.get('SL_BOT_DIRECTOR1', None),
    'director2': os.environ.get('SL_BOT_DIRECTOR2', None)
}
# Enable judging tab
JUDGING_ENABLED = False

# Can Hackers start a request on the hardware lab?
# HACKERS_CAN_REQUEST = False

# Enable dubious separate pipeline (disabled by default)
DUBIOUS_ENABLED = True


# Enable blacklist separate pipeline (disabled by default)
BLACKLIST_ENABLED = True

SUPPORTED_RESUME_EXTENSIONS = ['.pdf']

# Mentor/Volunteer applications can expire if they are invited, set to False to not
MENTOR_EXPIRES = False
VOLUNTEER_EXPIRES = False

DISCORD_HACKATHON = False
HYBRID_HACKATHON = False
N_MAX_LIVE_HACKERS = 600

SERVER_EMAIL = 'HackUPC Team <noreply@hackupc.com>'

CODE_CONDUCT_LINK = 'https://legal.hackersatupc.org/hackupc/code_of_conduct'
LEGAL_LINK = 'https://legal.hackersatupc.org/hackupc/legal_notice'
PRIVACY_LINK = 'https://legal.hackersatupc.org/hackupc/privacy_and_cookies'
TERMS_LINK = 'https://legal.hackersatupc.org/hackupc/terms_and_conditions'
