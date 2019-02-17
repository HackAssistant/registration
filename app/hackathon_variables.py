# HACKATHON PERSONALIZATION
import os

from django.utils import timezone

HACKATHON_NAME = 'Hacklahoma2020'
# What's the name for the application
HACKATHON_APPLICATION_NAME = 'Hacklahoma 2020 Registration'
# Hackathon timezone
TIME_ZONE = 'CST'
# This description will be used on the html and sharing meta tags
HACKATHON_DESCRIPTION = 'Hacklahoma is the original Oklahoma hackathon!'
# Domain where application is deployed, can be set by env variable
HACKATHON_DOMAIN = os.environ.get('DOMAIN', 'localhost:8000')
# Hackathon contact email: where should all hackers contact you. It will also be used as a sender for all emails
HACKATHON_CONTACT_EMAIL = 'team@hacklahoma.org'
# Hackathon logo url, will be used on all emails
HACKATHON_LOGO_URL = 'https://avatars2.githubusercontent.com/u/33712329?s=200&v=4' # Needs to be Updated for Hacklahoma

HACKATHON_OG_IMAGE = 'https://hackcu.org/img/hackcu_ogimage870x442.png'         # Needs to be Updated for Hacklahoma
# (OPTIONAL) Track visits on your website
# HACKATHON_GOOGLE_ANALYTICS = 'UA-7777777-2'
# (OPTIONAL) Hackathon twitter user
HACKATHON_TWITTER_ACCOUNT = 'hacklahoma'
# (OPTIONAL) Hackathon Facebook page
HACKATHON_FACEBOOK_PAGE = 'hacklahoma'
# (OPTIONAL) Github Repo for this project (so meta)
HACKATHON_GITHUB_REPO = 'https://github.com/hackassistant/registration/'        # Needs to be Updated for Hacklahoma

# (OPTIONAL) Applications deadline
# HACKATHON_APP_DEADLINE = timezone.datetime(2018, 2, 24, 3, 14, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) When to arrive at the hackathon
HACKATHON_ARRIVE = 'Check in opens at 9:00 AM and closes at 12:00 PM on Saturday [DATE TBD], ' \
                   'Opening ceremony begins at 12:00 PM.'

# (OPTIONAL) When to arrive at the hackathon
HACKATHON_LEAVE = 'Project submissions are due at 12:00 PM on Sunday [DATE TBD]. Judging and project expo will begin at 1:00 PM.' \
                  'Closing ceremony will be held on Sunday at TBD.'
# (OPTIONAL) Hackathon live page
# HACKATHON_LIVE_PAGE = 'https://gerard.space/live'

# (OPTIONAL) Regex to automatically match organizers emails and set them as organizers when signing up
REGEX_HACKATHON_ORGANIZER_EMAIL = '^.*@gerard\.space$'

# (OPTIONAL) Sends 500 errors to email whilst in production mode.
HACKATHON_DEV_EMAILS = []

# Reimbursement configuration
REIMBURSEMENT_ENABLED = True
CURRENCY = '$'
REIMBURSEMENT_EXPIRY_DAYS = 5
REIMBURSEMENT_REQUIREMENTS = 'You have to submit a project and demo it during the event, as well as create a social media post with #hacklahoma20 in order to be reimbursed.'
                            'Our University will additionally require you to complete a reimbursement form at the event.'
REIMBURSEMENT_DEADLINE = timezone.datetime(2018, 2, 24, 3, 14, tzinfo=timezone.pytz.timezone(TIME_ZONE))

# (OPTIONAL) Max team members. Defaults to 4
TEAMS_ENABLED = True
HACKATHON_MAX_TEAMMATES = 4

# (OPTIONAL) Code of conduct link
# CODE_CONDUCT_LINK = "https://static.mlh.io/docs/mlh-code-of-conduct.pdf"

# (OPTIONAL) Slack credentials
# Highly recommended to create a separate user account to extract the token from
SLACK = {
    'team': os.environ.get('SL_TEAM', 'test'),
    # Get it here: https://api.slack.com/custom-integrations/legacy-tokens
    'token': os.environ.get('SL_TOKEN', None)
}

# (OPTIONAL) Logged in cookie
# This allows to store an extra cookie in the browser to be shared with other application on the same domain
LOGGED_IN_COOKIE_DOMAIN = '.gerard.space'
LOGGED_IN_COOKIE_KEY = 'hackassistant_logged_in'

# Hardware configuration
HARDWARE_ENABLED = False
# Hardware request time length (in minutes)
HARDWARE_REQUEST_TIME = 15
# Can Hackers start a request on the hardware lab?
# HACKERS_CAN_REQUEST = False
