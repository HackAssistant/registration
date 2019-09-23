from django.conf import settings
from django.contrib import admin
from django.db.models import Func
from django.forms import forms
from django.urls import reverse as django_reverse
from django.utils import timezone
from django.utils.functional import keep_lazy_text

from offer.models import Code


def reverse(viewname, args=None, kwargs=None, request=None, format=None,
            **extra):
    """
    Same as `django.urls.reverse`, but optionally takes a request
    and returns a fully qualified URL, using the request to get the base URL.
    """
    if format is not None:
        kwargs = kwargs or {}
        kwargs['format'] = format
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

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


class Round4(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 4)'


def application_timeleft():
    deadline = getattr(settings, 'HACKATHON_APP_DEADLINE', None)
    if deadline:
        return deadline - timezone.now()
    else:
        return None


def is_app_closed():
    timeleft = application_timeleft()
    if timeleft and timeleft != timezone.timedelta():
        return timeleft < timezone.timedelta()
    return False


def get_substitutions_templates():
    return {'h_name': getattr(settings, 'HACKATHON_NAME', None),
            'h_app_name': getattr(settings, 'HACKATHON_APPLICATION_NAME', None),
            'h_contact_email': getattr(settings, 'HACKATHON_CONTACT_EMAIL', None),
            'h_max_team': getattr(settings, 'HACKATHON_MAX_TEAMMATES', 4),
            'h_team_enabled': getattr(settings, 'TEAMS_ENABLED', False),
            'h_domain': getattr(settings, 'HACKATHON_DOMAIN', None),
            'h_description': getattr(settings, 'HACKATHON_DESCRIPTION', None),
            'h_ga': getattr(settings, 'HACKATHON_GOOGLE_ANALYTICS', None),
            'h_tw': getattr(settings, 'HACKATHON_TWITTER_ACCOUNT', None),
            'h_repo': getattr(settings, 'HACKATHON_GITHUB_REPO', None),
            'h_app_closed': is_app_closed(),
            'h_app_timeleft': application_timeleft(),
            'h_arrive': getattr(settings, 'HACKATHON_ARRIVE', None),
            'h_leave': getattr(settings, 'HACKATHON_LEAVE', None),
            'h_logo': getattr(settings, 'HACKATHON_LOGO_URL', None),
            'h_fb': getattr(settings, 'HACKATHON_FACEBOOK_PAGE', None),
            'h_ig': getattr(settings, 'HACKATHON_INSTAGRAM_ACCOUNT', None),
            'h_yt': getattr(settings, 'HACKATHON_YOUTUBE_PAGE', None),
            'h_me': getattr(settings, 'HACKATHON_MEDIUM_ACCOUNT', None),
            'h_live': getattr(settings, 'HACKATHON_LIVE_PAGE', None),
            'h_theme_color': getattr(settings, 'HACKATHON_THEME_COLOR', None),
            'h_og_image': getattr(settings, 'HACKATHON_OG_IMAGE', None),
            'h_currency': getattr(settings, 'CURRENCY', '$'),
            'h_r_requirements': getattr(settings, 'REIMBURSEMENT_REQUIREMENTS', None),
            'h_r_days': getattr(settings, 'REIMBURSEMENT_EXPIRY_DAYS', None),
            'h_r_enabled': getattr(settings, 'REIMBURSEMENT_ENABLED', False),
            'h_hw_enabled': getattr(settings, 'HARDWARE_ENABLED', False),
            'h_b_picture': getattr(settings, 'BAGGAGE_PICTURE', False),
            'h_oauth_providers': getattr(settings, 'OAUTH_PROVIDERS', {}),
            'h_judging': getattr(settings, 'JUDGING_ENABLED', {}),
            'h_hw_hacker_request': getattr(settings, 'HACKERS_CAN_REQUEST', True),
            'h_dubious_enabled': getattr(settings, 'DUBIOUS_ENABLED', False),
            }


def get_user_substitutions(request):
    user = getattr(request, 'user', None)
    if not user:
        return {}
    return {
        'application': getattr(user, 'application', None),
        'reimbursement': getattr(user, 'reimbursement', None),
        'user': user
    }


def hackathon_vars_processor(request):
    c = get_substitutions_templates()
    c.update(get_user_substitutions(request))
    c.update({'slack_enabled': settings.SLACK.get('token', None) and settings.SLACK.get('team', None)})
    return c


def validate_url(data, query):
    """
    Checks if the given url contains the specified query. Used for custom url validation in the ModelForms
    :param data: full url
    :param query: string to search within the url
    :return:
    """
    if data and query not in data:
        raise forms.ValidationError('Please enter a valid {} url'.format(query))


@keep_lazy_text
def lazy_format(s, f):
    return format(s, f)


def hacker_tabs(user):
    app = getattr(user, 'application', None)
    l = [('Home', reverse('dashboard'),
          'Invited' if app and user.application.needs_action() else False), ]
    if user.email_verified and app and getattr(settings, 'TEAMS_ENABLED', False) and app.can_join_team():
        l.append(('Team', reverse('teams'), False))
    if app:
        l.append(('Application', reverse('application'), False))

    if app and getattr(user, 'reimbursement', None) and settings.REIMBURSEMENT_ENABLED:
        l.append(('Travel', reverse('reimbursement_dashboard'),
                  'Pending' if user.reimbursement.needs_action() else False))

    if app and app.is_confirmed and Code.objects.filter(user_id=user.id).exists():
        l.append(('Offers', reverse('codes'), False))

    return l
