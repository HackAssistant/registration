from django.conf import settings
from django.contrib import admin
from django.db.models import Func
from django.forms import forms
from django.urls import reverse as django_reverse
from django.utils import timezone
from django.utils.functional import keep_lazy_text
from datetime import datetime

import os

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from google.auth import jwt, crypt


from offer.models import Code


def reverse(viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Same as `django.urls.reverse`, but optionally takes a request
    and returns a fully qualified URL, using the request to get the base URL.
    """
    if format is not None:
        kwargs = kwargs or {}
        kwargs["format"] = format
    url = django_reverse(viewname, args=args, kwargs=kwargs, **extra)
    if request:
        return request.build_absolute_uri(url)
    return url


def create_modeladmin(modeladmin, model, name=None):
    """
    Allows to register a model in multiple views
    http://stackoverflow.com/questions/2223375/multiple-modeladmins-views-
    for-same-model-in-django-admin
    """

    class Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {"__module__": "", "Meta": Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


class Round4(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 4)"


def application_timeleft(app_type="H"):
    if app_type == "H":
        deadline = getattr(settings, "HACKATHON_APP_DEADLINE", None)
    elif app_type == "V":
        deadline = getattr(settings, "VOLUNTEER_APP_DEADLINE", None)
    elif app_type == "M":
        deadline = getattr(settings, "MENTOR_APP_DEADLINE", None)
    else:
        deadline = getattr(settings, "HACKATHON_APP_DEADLINE", None)

    if deadline:
        return deadline - timezone.now()
    else:
        return None


def is_app_closed(app_type="H"):
    timeleft = application_timeleft(app_type)
    if timeleft and timeleft != timezone.timedelta():
        return timeleft < timezone.timedelta()
    return False


def is_online_checkin_closed():
    opens = getattr(settings, "ONLINE_CHECKIN", None)
    if opens:
        closes = opens + timezone.timedelta(days=1)
        return opens <= timezone.now() <= closes
    else:
        return False


def get_substitutions_templates():
    return {
        "h_name": getattr(settings, "HACKATHON_NAME", None),
        "h_app_name": getattr(settings, "HACKATHON_APPLICATION_NAME", None),
        "h_contact_email": getattr(settings, "HACKATHON_CONTACT_EMAIL", None),
        "h_max_team": getattr(settings, "HACKATHON_MAX_TEAMMATES", 4),
        "h_team_enabled": getattr(settings, "TEAMS_ENABLED", False),
        "h_domain": getattr(settings, "HACKATHON_DOMAIN", None),
        "h_description": getattr(settings, "HACKATHON_DESCRIPTION", None),
        "h_ga": getattr(settings, "HACKATHON_GOOGLE_ANALYTICS", None),
        "h_tw": getattr(settings, "HACKATHON_TWITTER_ACCOUNT", None),
        "h_repo": getattr(settings, "HACKATHON_GITHUB_REPO", None),
        "h_app_closed": is_app_closed(),
        "h_app_volunteer_closed": is_app_closed("V"),
        "h_app_mentor_closed": is_app_closed("M"),
        "h_app_sponsor_closed": is_app_closed("S"),
        "h_app_timeleft": application_timeleft(),
        "h_app_volunteer_timeleft": application_timeleft("V"),
        "h_app_mentor_timeleft": application_timeleft("M"),
        "h_app_sponsor_timeleft": application_timeleft("S"),
        "h_arrive": getattr(settings, "HACKATHON_ARRIVE", None),
        "h_leave": getattr(settings, "HACKATHON_LEAVE", None),
        "h_logo": getattr(settings, "HACKATHON_LOGO_URL", None),
        "h_fb": getattr(settings, "HACKATHON_FACEBOOK_PAGE", None),
        "h_ig": getattr(settings, "HACKATHON_INSTAGRAM_ACCOUNT", None),
        "h_yt": getattr(settings, "HACKATHON_YOUTUBE_PAGE", None),
        "h_me": getattr(settings, "HACKATHON_MEDIUM_ACCOUNT", None),
        "h_live": getattr(settings, "HACKATHON_LIVE_PAGE", None),
        "h_theme_color": getattr(settings, "HACKATHON_THEME_COLOR", None),
        "h_og_image": getattr(settings, "HACKATHON_OG_IMAGE", None),
        "h_currency": getattr(settings, "CURRENCY", "$"),
        "h_r_requirements": getattr(settings, "REIMBURSEMENT_REQUIREMENTS", None),
        "h_r_days": getattr(settings, "REIMBURSEMENT_EXPIRY_DAYS", None),
        "h_r_enabled": getattr(settings, "REIMBURSEMENT_ENABLED", False),
        "h_hw_enabled": getattr(settings, "HARDWARE_ENABLED", False),
        "h_b_picture": getattr(settings, "BAGGAGE_PICTURE", False),
        "h_oauth_providers": getattr(settings, "OAUTH_PROVIDERS", {}),
        "h_judging": getattr(settings, "JUDGING_ENABLED", {}),
        "h_hw_hacker_request": getattr(settings, "HACKERS_CAN_REQUEST", True),
        "h_dubious_enabled": getattr(settings, "DUBIOUS_ENABLED", False),
        "h_blacklist_enabled": getattr(settings, "BLACKLIST_ENABLED", True),
        "h_discord": getattr(settings, "DISCORD_HACKATHON", False),
        "captcha_site_key": getattr(settings, "GOOGLE_RECAPTCHA_SITE_KEY", ""),
        "h_hybrid": getattr(settings, "HYBRID_HACKATHON", False),
        "n_live_max_hackers": getattr(settings, "N_MAX_LIVE_HACKERS", 0),
        "h_online_checkin": is_online_checkin_closed(),
    }


def get_user_substitutions(request):
    user = getattr(request, "user", None)
    if not user:
        return {}
    return {
        "application": getattr(user, "application", None),
        "reimbursement": getattr(user, "reimbursement", None),
        "user": user,
    }


def hackathon_vars_processor(request):
    c = get_substitutions_templates()
    c.update(get_user_substitutions(request))
    c.update(
        {
            "slack_enabled": settings.SLACK.get("token", None)
            and settings.SLACK.get("team", None),
            "mentor_expires": settings.MENTOR_EXPIRES,
            "volunteer_expires": settings.VOLUNTEER_EXPIRES,
        }
    )
    discord = getattr(settings, "DISCORD_HACKATHON", False)
    c.update({"h_discord": discord})
    return c


def validate_url(data, query):
    """
    Checks if the given url contains the specified query. Used for custom url validation in the ModelForms
    :param data: full url
    :param query: string to search within the url
    :return:
    """
    if data and query not in data:
        if query:
            query += " "
        raise forms.ValidationError("Enter a valid {}URL.".format(query))


@keep_lazy_text
def lazy_format(s, f):
    return format(s, f)


def hacker_tabs(user):
    app = getattr(user, "application", None)
    tabs_list = [
        (
            "Home",
            reverse("dashboard"),
            "Invited" if app and user.application.needs_action() else False,
        ),
    ]
    if (
        user.email_verified
        and app
        and getattr(settings, "TEAMS_ENABLED", False)
        and app.can_join_team()
    ):
        tabs_list.append(("Team", reverse("teams"), False))
    if app:
        tabs_list.append(("Application", reverse("application"), False))

    if app and getattr(user, "reimbursement", None) and settings.REIMBURSEMENT_ENABLED:
        tabs_list.append(
            (
                "Travel",
                reverse("reimbursement_dashboard"),
                "Pending" if user.reimbursement.needs_action() else False,
            )
        )

    if app and app.is_confirmed and Code.objects.filter(user_id=user.id).exists():
        tabs_list.append(("Offers", reverse("codes"), False))

    return tabs_list


def generateGTicketUrl(qrValue: str):
    """
    Generates a url for the google ticketing system
    :param qrValue: the value of the qr code
    :return: url
    """
    generic = GenericPass()
    objSufix = qrValue  # uuid.uuid4().hex
    issuer_id = os.environ.get("GOOGLE_WALLET_ISSUER_ID", "")
    class_suffix = os.environ.get("GOOGLE_WALLET_CLASS_SUFFIX", "")
    cardObject = {
        "id": f"{issuer_id}.{objSufix}",
        "classId": f"{issuer_id}.{class_suffix}",
        "state": "ACTIVE",
        "heroImage": {
            "sourceUri": {"uri": "https://i.ibb.co/CwwGY33/Fondo-2.png"},
            "contentDescription": {
                "defaultValue": {
                    "language": "en-US",
                    "value": f"{settings.HACKATHON_NAME} {datetime.now().year} is here!",
                }
            },
        },
        "textModulesData": [
            {
                "header": "Disclaimer",
                "body": "This is a copy of the official ticket, do not treat this as the official ticket "
                "since it is not updated in real time.",
                "id": "TEXT_MODULE_ID",
            }
        ],
        "linksModuleData": {
            "uris": [
                {
                    "uri": "https://live.hackupc.com/",
                    "description": "Live HackUPC",
                    "id": "LINK_MODULE_URI_ID",
                },
                {
                    "uri": "https://my.hackupc.com/",
                    "description": "MyHackUPC",
                    "id": "LINK_MODULE_URI_ID",
                },
            ]
        },
        "imageModulesData": [
            {
                "mainImage": {
                    "sourceUri": {"uri": "https://hackupc.com/ogimage.png"},
                    "contentDescription": {
                        "defaultValue": {"language": "en-US", "value": "Event picture"}
                    },
                },
                "id": "IMAGE_MODULE_ID",
            }
        ],
        "barcode": {
            "type": "QR_CODE",
            "value": objSufix,
        },
        "cardTitle": {
            "defaultValue": {"language": "en-US", "value": "An event of Hackers@UPC"}
        },
        "header": {"defaultValue": {"language": "en-US", "value": "HackUPC 2024"}},
        "hexBackgroundColor": "#fff",
        "logo": {
            "sourceUri": {
                "uri": "https://my.hackupc.com/static/img/favicon/apple-touch-icon.0d0372730c66.png"
            },
            "contentDescription": {
                "defaultValue": {"language": "en-US", "value": "HackUPC Logo"}
            },
        },
    }

    generic.create_object(issuer_id, objSufix, cardObject)
    return generic.create_jwt_new_objects(issuer_id, class_suffix, cardObject)


#
# Copyright 2022 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#


class GenericPass:
    """Class for creating and managing Generic passes in Google Wallet.

    Attributes:
        key_file_path: Path to service account key file from Google Cloud
            Console. Environment variable: GOOGLE_APPLICATION_CREDENTIALS.
        base_url: Base URL for Google Wallet API requests.
    """

    def __init__(self):
        self.key_file_path = os.environ.get(
            "GOOGLE_WALLET_APPLICATION_CREDENTIALS", "/path/to/key.json"
        )
        self.base_url = "https://walletobjects.googleapis.com/walletobjects/v1"
        self.batch_url = "https://walletobjects.googleapis.com/batch"
        self.class_url = f"{self.base_url}/genericClass"
        self.object_url = f"{self.base_url}/genericObject"

        # Set up authenticated client
        self.auth()

    # [END setup]

    # [START auth]
    def auth(self):
        """Create authenticated HTTP client using a service account file."""
        self.credentials = Credentials.from_service_account_file(
            self.key_file_path,
            scopes=["https://www.googleapis.com/auth/wallet_object.issuer"],
        )

        self.http_client = AuthorizedSession(self.credentials)

    # [END auth]

    # [START createObject]
    def create_object(
        self, issuer_id: str, object_suffix: str, cardObject: dict
    ) -> str:
        """Create an object.

        Args:
            issuer_id (str): The issuer ID being used for this request.
            class_suffix (str): Developer-defined unique ID for the pass class.
            object_suffix (str): Developer-defined unique ID for the pass object.

        Returns:
            The pass object ID: f"{issuer_id}.{object_suffix}"
        """

        # Check if the object exists
        response = self.http_client.get(
            url=f"{self.object_url}/{issuer_id}.{object_suffix}"
        )

        if response.status_code == 200:
            print(
                f"[GOOGLE_WALLET]: Object {issuer_id}.{object_suffix} already exists!"
            )
            # print(response.text)
            return f"{issuer_id}.{object_suffix}"
        elif response.status_code == 404:
            # Object does not exist, let's create it
            # See link below for more information on required properties
            # https://developers.google.com/wallet/generic/rest/v1/genericobject
            new_object = cardObject

            # Create the object
            response = self.http_client.post(url=self.object_url, json=new_object)

            print("Object created successfully!")

            return response.json().get("id")
        else:
            # Something else went wrong...
            print("[GOOGLE_WALLET]:", response.text)
            return f"{issuer_id}.{object_suffix}"

    # [END createObject]

    # [START jwtNew]
    def create_jwt_new_objects(
        self,
        issuer_id: str,
        class_suffix: str,
        cardObject: dict,
    ) -> str:
        """Generate a signed JWT that creates a new pass class and object.

        When the user opens the "Add to Google Wallet" URL and saves the pass to
        their wallet, the pass class and object defined in the JWT are
        created. This allows you to create multiple pass classes and objects in
        one API call when the user saves the pass to their wallet.

        Args:
            issuer_id (str): The issuer ID being used for this request.
            class_suffix (str): Developer-defined unique ID for the pass class.
            object_suffix (str): Developer-defined unique ID for the pass object.

        Returns:
            An "Add to Google Wallet" link.
        """

        # See link below for more information on required properties
        # https://developers.google.com/wallet/generic/rest/v1/genericclass
        new_class = {"id": f"{issuer_id}.{class_suffix}"}

        # See link below for more information on required properties
        # https://developers.google.com/wallet/generic/rest/v1/genericobject
        new_object = cardObject

        # Create the JWT claims
        claims = {
            "iss": self.credentials.service_account_email,
            "aud": "google",
            "origins": ["my.hackupc.com"],
            "typ": "savetowallet",
            "payload": {
                # The listed classes and objects will be created
                "genericClasses": [new_class],
                "genericObjects": [new_object],
            },
        }

        # The service account credentials are used to sign the JWT
        signer = crypt.RSASigner.from_service_account_file(self.key_file_path)
        token = jwt.encode(signer, claims).decode("utf-8")

        return f"https://pay.google.com/gp/v/save/{token}"

    # [END jwtNew]


def isset(variable):
    try:
        variable
    except NameError:
        return False
    else:
        return True
