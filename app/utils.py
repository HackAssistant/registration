from django.conf import settings
from django.contrib import admin
from django.db.models import Func
from django.forms import forms
from django.urls import reverse as django_reverse
from django.utils import timezone
from django.utils.functional import keep_lazy_text
from datetime import datetime

import os

from app.gwallet.eventticket import EventTicket


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


def is_event_weekend():
    start = getattr(settings, "HACKATHON_START_DAY", None)
    end = getattr(settings, "HACKATHON_END_DAY", None)
    if not start or not end:
        return False
    return start <= timezone.localdate() <= end


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
        "h_is_event_weekend": is_event_weekend(),
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
        "h_r_days": getattr(settings, "REIMBURSEMENT_EXPIRY_DATE", None),
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
    issuer_id = os.environ.get("GOOGLE_WALLET_ISSUER_ID", "")
    class_suffix = os.environ.get("GOOGLE_WALLET_CLASS_SUFFIX", "")
    object_suffix = os.environ.get("GOOGLE_WALLET_PASS_SUFFIX", "") + qrValue
    class_data = {
        "id": f"{issuer_id}.{class_suffix}",
        "eventId": f"{issuer_id}.{class_suffix}",
        "reviewStatus": "UNDER_REVIEW",
        "issuerName": "Hackers@UPC",
        "localizedIssuerName": {
            "defaultValue": {
                "language": "en-US",
                "value": "Hackers@UPC",
            },
        },
        "logo": {
            "sourceUri": {
                "uri": "https://i.ibb.co/g2GGdMB/Copy-of-Isotipo-B-6.png",
            },
            "contentDescription": {
                "defaultValue": {
                    "language": "en-US",
                    "value": "HackUPC favicon",
                },
            },
        },
        "eventName": {
            "defaultValue": {
                "language": "en-US",
                "value": f"{settings.HACKATHON_NAME} {datetime.now().year}",
            },
        },
        "imageModulesData": [
            {
                "mainImage": {
                    "sourceUri": {"uri": "https://hackupc.com/og_image2026.png"},
                    "contentDescription": {
                        "defaultValue": {"language": "en-US", "value": "Event picture"}
                    },
                },
                "id": "main_banner",
            }
        ],
        "textModulesData": [
            {
                "header": "Disclaimer",
                "body": "This is a copy of the official ticket, do not treat this as the official ticket "
                "since it is not updated in real time.",
                "id": "TEXT_MODULE_ID",
            },
        ],
        "linksModuleData": {
            "uris": [
                {
                    "uri": "https://live.hackupc.com/",
                    "description": "Live HackUPC",
                    "id": "link_live_hackupc",
                },
                {
                    "uri": "https://my.hackupc.com/",
                    "description": "MyHackUPC",
                    "id": "link_my_hackupc",
                },
            ]
        },
        "venue": {
            "name": {
                "defaultValue": {
                    "language": "en-US",
                    "value": "Campus Nord UPC",
                },
            },
            "address": {
                "defaultValue": {
                    "language": "en-US",
                    "value": "FIB Facultat d'Informàtica de Barcelona, Edifici A6 del Campus Nord, C/Jordi Girona,\
                          1-3, 08034 Barcelona",
                },
            },
        },
        "dateTime": {"start": "2026-04-24T16:00", "end": "2026-04-26T17:00"},
        "reviewStatus": "UNDER_REVIEW",
        "hexBackgroundColor": "#AADEFE",
        "heroImage": {
            "sourceUri": {
                "uri": "https://i.ibb.co/nN4GxfFt/imatge-wallet.png",
            },
            "contentDescription": {
                "defaultValue": {
                    "language": "en-US",
                    "value": "HackUPC 2026 Banner",
                },
            },
        },
    }
    pass_data = {
        "id": f"{issuer_id}.{object_suffix}",
        "classId": f"{issuer_id}.{class_suffix}",
        "issuerName": "Hackers@UPC",
        "state": "ACTIVE",
        "barcode": {
            "type": "QR_CODE",
            "value": qrValue,
        },
    }
    ticket = EventTicket()
    ticket.create_class(
        issuer_id=issuer_id, class_suffix=class_suffix, class_data=class_data
    )
    ticket.create_object(
        issuer_id=issuer_id,
        class_suffix=class_suffix,
        object_suffix=object_suffix,
        object_pass=pass_data,
    )
    return ticket.create_jwt_new_objects(
        issuer_id=issuer_id, class_suffix=class_suffix, object_suffix=object_suffix
    )


def isset(variable):
    try:
        variable
    except NameError:
        return False
    else:
        return True
