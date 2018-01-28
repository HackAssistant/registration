from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone

from app.views import TabsView
from applications.models import Application, STATUS, APP_CONFIRMED, GENDERS
from user.mixins import is_organizer, IsOrganizerMixin

STATUS_DICT = dict(STATUS)
GENDER_DICT = dict(GENDERS)


@is_organizer
def app_stats_api(request):
    # Status analysis
    status_count = Application.objects.all().values('status') \
        .annotate(applications=Count('status'))
    status_count = map(lambda x: dict(status_name=STATUS_DICT[x['status']], **x), status_count)

    gender_count = Application.objects.all().values('gender') \
        .annotate(applications=Count('gender'))
    gender_count = map(lambda x: dict(gender_name=GENDER_DICT[x['gender']], **x), gender_count)

    shirt_count = Application.objects.values('tshirt_size') \
        .annotate(applications=Count('tshirt_size'))
    shirt_count_confirmed = Application.objects.filter(status=APP_CONFIRMED).values('tshirt_size') \
        .annotate(applications=Count('tshirt_size'))

    diet_count = Application.objects.values('diet') \
        .annotate(applications=Count('diet'))
    diet_count_confirmed = Application.objects.filter(status=APP_CONFIRMED).values('diet') \
        .annotate(applications=Count('diet'))
    other_diets = Application.objects.values('other_diet')

    timeseries = Application.objects.all().annotate(date=TruncDate('submission_date')).values('date').annotate(
        applications=Count('date'))
    return JsonResponse(
        {
            'update_time': timezone.now(),
            'status': list(status_count),
            'shirt_count': list(shirt_count),
            'shirt_count_confirmed': list(shirt_count_confirmed),
            'timeseries': list(timeseries),
            'gender': list(gender_count),
            'diet': list(diet_count),
            'diet_confirmed': list(diet_count_confirmed),
            'other_diet': ';'.join([el['other_diet'] for el in other_diets if el['other_diet']])
        }
    )


class AppStats(IsOrganizerMixin, TabsView):
    template_name = 'application_stats.html'

    def get_context_data(self, **kwargs):
        return {}
