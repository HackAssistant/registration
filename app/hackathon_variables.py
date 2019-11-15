# HACKATHON PERSONALIZATION
import os

from django.utils import timezone

HACKATHON_NAME = 'Hack Kosice'
# What's the name for the application
HACKATHON_APPLICATION_NAME = 'Hack Kosice registration'
# Hackathon timezone
TIME_ZONE = 'CET'
# This description will be used on the html and sharing meta tags
HACKATHON_DESCRIPTION = 'Hackathon in Kosice, Slovakia: 24 hours, 250 hackers, 1 spirit. ' \
                        'Come to meet the best hackers, eat the best free food, invent something groundbreaking.'
# Domain where application is deployed, can be set by env variable
HACKATHON_DOMAIN = os.environ.get('DOMAIN', 'apply-dev.hackkosice.com')
# Hackathon contact email: where should all hackers contact you. It will also be used as a sender for all emails
HACKATHON_CONTACT_EMAIL = 'contact@hackkosice.com'
# Hackathon logo url, will be used on all emails
HACKATHON_LOGO_URL = 'https://hackkosice.com/wp-content/uploads/2018/10/logo_purpleldpi.png'

HACKATHON_OG_IMAGE = 'https://hackkosice.com/wp-content/uploads/2018/11/og_image_date.png'
# (OPTIONAL) Track visits on your website
# Web Analytics code
HACKATHON_GOOGLE_ANALYTICS = 'UA-117942945-2'
# (OPTIONAL) Hackathon twitter user
HACKATHON_TWITTER_ACCOUNT = 'hackkosice'
# (OPTIONAL) Hackathon Facebook page
HACKATHON_FACEBOOK_PAGE = 'hackkosice'
# (OPTIONAL) Hackathon Instagram page
HACKATHON_INSTAGRAM_PAGE = 'hackkosice'
# (OPTIONAL) Github Repo for this project (so meta)
HACKATHON_GITHUB_REPO = 'https://github.com/hackkosice/registration/'

# (OPTIONAL) Applications opening date
HACKATHON_APP_OPENING = timezone.datetime(2019, 11, 15, 18, 00, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) Applications deadline
HACKATHON_APP_DEADLINE = timezone.datetime(2020, 3, 13, 0, 0, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) When to arrive at the hackathon
# Registration and Closing ceremony times (make sure we won't need to change them)
HACKATHON_ARRIVE = 'Registration opens at 8:30 and closes at 9:30 on Saturday March 28th, ' \
                   'the opening ceremony will be at 10:00.'

# (OPTIONAL) When to arrive at the hackathon
HACKATHON_LEAVE = 'Closing ceremony will be held on Sunday March 29th from 18:30 to 19:30. ' \
                  'However, the projects demo fair will be held from 15:00 to 17:00.'
# (OPTIONAL) Hackathon live page
HACKATHON_LIVE_PAGE = 'https://hackkosice.com/'

# (OPTIONAL) Regex to automatically match organizers emails and set them as organizers when signing up
REGEX_HACKATHON_ORGANIZER_EMAIL = '^.*@hackkosice\.com$'

# (OPTIONAL) Sends 500 errors to email whilst in production mode.
HACKATHON_DEV_EMAILS = ['dev@hackkosice.com']

# Reimbursement configuration
REIMBURSEMENT_ENABLED = True
CURRENCY = '\u20ac'
REIMBURSEMENT_EXPIRY_DAYS = 25
REIMBURSEMENT_AMOUNTS = 'We provide travel reimbursements if you are coming from abroad. ' \
                        'Up to 20\u20ac if you are coming from Czech/Poland/Hungary/Austria/Ukraine ' \
                        'and up to 50\u20ac otherwise (excluding Slovakia).'
REIMBURSEMENT_REQUIREMENTS = 'To get reimbursed, you need to attend the hackathon, ' \
                             'demo a project and submit travel receipts.'
REIMBURSEMENT_DEADLINE = timezone.datetime(2020, 4, 13, 0, 0, tzinfo=timezone.pytz.timezone(TIME_ZONE))

VISA_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSeo4Ilfof9zl0k1327XeX39HmPryC2kEok8JxbZyyr557cOSw/viewform"

# (OPTIONAL) Max team members. Defaults to 4
TEAMS_ENABLED = True
HACKATHON_MAX_TEAMMATES = 4

# (OPTIONAL) Code of conduct link
CODE_CONDUCT_LINK = "https://static.mlh.io/docs/mlh-code-of-conduct.pdf"
PRIVACY_POLICY_LINK = "https://hackkosice.com/privacy-policy"

# (OPTIONAL) Slack credentials
# Highly recommended to create a separate user account to extract the token from
SLACK = {
    'team': os.environ.get('SL_TEAM', 'test'),
    # Get it here: https://api.slack.com/custom-integrations/legacy-tokens
    'token': os.environ.get('SL_TOKEN', None)
}

# (OPTIONAL) Logged in cookie
# This allows to store an extra cookie in the browser to be shared with other application on the same domain
LOGGED_IN_COOKIE_DOMAIN = '.hackkosice.com'
LOGGED_IN_COOKIE_KEY = 'hackkosice_logged_in'

# Hardware configuration
HARDWARE_ENABLED = False
#Hardware request time length (in minutes)
HARDWARE_REQUEST_TIME = 15

# Check-in type expiration time in seconds
TYPE_EXPIRY = 3600
