import csv

from django.conf import settings
from django.contrib import admin
from django.db.models import Func
from django.forms import forms
from django.http import HttpResponse
from django.urls import reverse as django_reverse
from django.utils import timezone
from django.utils.functional import keep_lazy_text


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


# Code inspired by this snippet: https://gist.github.com/mgerring/3645889

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse()
        response['Content-Disposition'] = \
            'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field))
                   else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv


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
            'h_live': getattr(settings, 'HACKATHON_LIVE_PAGE', None),
            'h_theme_color': getattr(settings, 'HACKATHON_THEME_COLOR', None),
            'h_og_image': getattr(settings, 'HACKATHON_OG_IMAGE', None),
            'h_currency': getattr(settings, 'DEFAULT_CURRENCY', '$'),
            'h_r_requirements': getattr(settings, 'REIMBURSEMENT_REQUIREMENTS', None),
            'h_r_days': getattr(settings, 'REIMBURSEMENT_EXPIRACY_DAYS', None),
            'h_r_enabled': getattr(settings, 'REIMBURSEMENT_ENABLED', False),
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
    l = [('Application', reverse('dashboard'),
          'Invited' if getattr(user, 'application', None) and user.application.needs_action() else False), ]
    if getattr(user, 'reimbursement', None):
        l += [('Reimbursement', reverse('reimbursement_dashboard'),
               'Pending' if user.reimbursement.needs_action() else False), ]

    return l
