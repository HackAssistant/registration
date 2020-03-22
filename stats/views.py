from django.conf import settings
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from app.views import TabsView
from applications import models as a_models
from applications.models import Application, STATUS, APP_CONFIRMED, GENDERS
from user.mixins import is_organizer, IsOrganizerMixin

STATUS_DICT = dict(STATUS)
GENDER_DICT = dict(GENDERS)


def stats_tabs():
    tabs = [('Applications', reverse('app_stats'), False), ]
    if getattr(settings, 'REIMBURSEMENT_ENABLED', False):
        tabs.append(('Reimbursements', reverse('reimb_stats'), False))
    return tabs


@is_organizer
def reimb_stats_api(request):
    from reimbursement.models import Reimbursement, RE_STATUS, RE_DRAFT
    RE_STATUS_DICT = dict(RE_STATUS)
    # Status analysis
    status_count = Reimbursement.objects.all().values('status') \
        .annotate(reimbursements=Count('status'))
    status_count = map(lambda x: dict(status_name=RE_STATUS_DICT[x['status']], **x), status_count)

    total_apps = Application.objects.count()
    reimb_count = Reimbursement.objects.count()

    amounts = Reimbursement.objects.all().exclude(status=RE_DRAFT).values('status') \
        .annotate(final_amount=Sum('reimbursement_money'), max_amount=Sum('assigned_money'))
    amounts = map(lambda x: dict(status_name=RE_STATUS_DICT[x['status']], **x), amounts)

    return JsonResponse(
        {
            'update_time': timezone.now(),
            'reimb_count': reimb_count,
            'reimb_apps': {'Reimbursement needed': reimb_count, 'No reimbursement': total_apps - reimb_count},
            'status': list(status_count),
            'amounts': list(amounts),
        }
    )


@is_organizer
def app_stats_api(request):
    # Status analysis
    status_count = Application.objects.all().values('status') \
        .annotate(applications=Count('status'))
    status_count = map(lambda x: dict(status_name=STATUS_DICT[x['status']], **x), status_count)

    gender_count = Application.objects.all().values('gender') \
        .annotate(applications=Count('gender'))
    gender_count = map(lambda x: dict(gender_name=GENDER_DICT[x['gender']], **x), gender_count)

    origin_count = Application.objects.all().values('origin') \
        .annotate(applications=Count('origin')) \
        .filter(applications__gte=2)
    origin_count_confirmed = Application.objects.filter(status=APP_CONFIRMED).values('origin') \
        .annotate(applications=Count('origin')) \
        .filter(applications__gte=2)

    tshirt_dict = dict(a_models.TSHIRT_SIZES)
    shirt_count = map(
        lambda x: {'tshirt_size': tshirt_dict.get(x['tshirt_size'], 'Unknown'), 'applications': x['applications']},
        Application.objects.values('tshirt_size').annotate(applications=Count('tshirt_size'))
    )

    shirt_count_confirmed = map(
        lambda x: {'tshirt_size': tshirt_dict.get(x['tshirt_size'], 'Unknown'), 'applications': x['applications']},
        Application.objects.filter(status=APP_CONFIRMED).values('tshirt_size')
        .annotate(applications=Count('tshirt_size'))
    )

    diet_count = Application.objects.values('diet') \
        .annotate(applications=Count('diet'))
    diet_count_confirmed = Application.objects.filter(status=APP_CONFIRMED).values('diet') \
        .annotate(applications=Count('diet'))
    other_diets = Application.objects.filter(status=APP_CONFIRMED).values('other_diet')

    timeseries = Application.objects.all().annotate(date=TruncDate('submission_date')).values('date').annotate(
        applications=Count('date'))
    return JsonResponse(
        {
            'update_time': timezone.now(),
            'app_count': Application.objects.count(),
            'status': list(status_count),
            'shirt_count': list(shirt_count),
            'shirt_count_confirmed': list(shirt_count_confirmed),
            'timeseries': list(timeseries),
            'gender': list(gender_count),
            'origin': list(origin_count),
            'origin_confirmed': list(origin_count_confirmed),
            'diet': list(diet_count),
            'diet_confirmed': list(diet_count_confirmed),
            'other_diet': '<br>'.join([el['other_diet'] for el in other_diets if el['other_diet']])
        }
    )


class AppStats(IsOrganizerMixin, TabsView):
    template_name = 'application_stats.html'

    def get_current_tabs(self):
        return stats_tabs()


class ReimbStats(IsOrganizerMixin, TabsView):
    template_name = 'reimbursement_stats.html'

    def get_current_tabs(self):
        return stats_tabs()
