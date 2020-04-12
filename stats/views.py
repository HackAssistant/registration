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
from user.models import User

from collections import defaultdict

STATUS_DICT = dict(STATUS)
GENDER_DICT = dict(GENDERS)


def stats_tabs():
    tabs = [('Applications', reverse('app_stats'), False), ('Users', reverse('users_stats'), False)]
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
    tshirt_dict = dict(a_models.TSHIRT_SIZES)
    diets_dict = dict(a_models.DIETS)
    applications = list(Application.objects.all())
    status_count = defaultdict(int)
    gender_count = defaultdict(int)
    origin_count = defaultdict(int)
    origin_count_confirmed = defaultdict(int)
    university_count = defaultdict(int)
    university_count_confirmed = defaultdict(int)
    grad_year_count = defaultdict(int)
    grad_year_count_confirmed = defaultdict(int)
    degree_count = defaultdict(int)
    degree_count_confirmed = defaultdict(int)
    first_timer_count = defaultdict(int)
    first_timer_count_confirmed = defaultdict(int)
    shirt_count = defaultdict(int)
    shirt_count_confirmed = defaultdict(int)
    diet_count = defaultdict(int)
    diet_count_confirmed = defaultdict(int)
    lennyface_count = defaultdict(int)
    lennyface_count_confirmed = defaultdict(int)
    resume_count = defaultdict(int)
    resume_count_confirmed = defaultdict(int)
    other_diet = []
    for a in applications:
        status_count[STATUS_DICT[a.status]] += 1
        gender_count[GENDER_DICT[a.gender]] += 1
        origin_count[a.origin] += 1
        university_count[a.university] += 1
        grad_year_count[a.graduation_year] += 1
        degree_count[a.degree] += 1
        first_timer_count[a.first_timer] += 1
        shirt_count[tshirt_dict[a.tshirt_size]] += 1
        diet_count[diets_dict[a.diet]] += 1
        lennyface_count[a.lennyface] += 1
        resume_count['Resume'] += a.resume != ""
        resume_count['No resume'] += a.resume == ""

        if a.status == APP_CONFIRMED:
            origin_count_confirmed[a.origin] += 1
            university_count_confirmed[a.university] += 1
            grad_year_count_confirmed[a.graduation_year] += 1
            degree_count_confirmed[a.degree] += 1
            first_timer_count_confirmed[a.first_timer] += 1
            shirt_count_confirmed[tshirt_dict[a.tshirt_size]] += 1
            diet_count_confirmed[diets_dict[a.diet]] += 1
            lennyface_count_confirmed[a.lennyface] += 1
            resume_count_confirmed['Resume'] += a.resume != ""
            resume_count_confirmed['No resume'] += a.resume == ""
            if a.diet == a_models.D_OTHER and a.other_diet:
                other_diet.append(a.other_diet)

    origin_count = [{'origin': x, 'applications': v} for (x, v) in sorted(origin_count.items(),
                                                                          key=lambda item: item[1])[-10:]]
    origin_count_confirmed = [{'origin': x, 'applications': v} for (x, v) in sorted(origin_count_confirmed.items(),
                                                                                    key=lambda item: item[1])[-10:]]

    university_count = [{'university': x, 'applications': v} for (x, v) in sorted(university_count.items(),
                                                                                  key=lambda item: item[1])[-10:]]
    university_count_confirmed = [{'university': x, 'applications': v} for (x, v) in
                                  sorted(university_count_confirmed.items(), key=lambda item: item[1])[-10:]]

    degree_count = [{'degree': x, 'applications': v} for (x, v) in
                    sorted(degree_count.items(), key=lambda item: item[1])[-10:]]
    degree_count_confirmed = [{'degree': x, 'applications': v} for (x, v) in
                              sorted(degree_count_confirmed.items(), key=lambda item: item[1])[-10:]]

    shirt_count = [{'tshirt': x, 'applications': v} for (x, v) in shirt_count.items()]
    shirt_count_confirmed = [{'tshirt': x, 'applications': v} for (x, v) in shirt_count_confirmed.items()]

    diet_count = [{'diet': x, 'applications': v} for (x, v) in diet_count.items()]
    diet_count_confirmed = [{'diet': x, 'applications': v} for (x, v) in diet_count_confirmed.items()]

    lennyface_count = [{'lennyface': x, 'applications': v} for (x, v) in
                       sorted(lennyface_count.items(), key=lambda item: item[1])[-5:]]
    lennyface_count_confirmed = [{'lennyface': x, 'applications': v} for (x, v) in
                                 sorted(lennyface_count_confirmed.items(), key=lambda item: item[1])[-5:]]

    timeseries = Application.objects.all().annotate(date=TruncDate('submission_date')).values('date').annotate(
        applications=Count('date'))

    return JsonResponse(
        {
            'timeseries': list(timeseries),
            'update_time': timezone.now(),
            'app_count': len(applications),
            'status': status_count,
            'tshirt': shirt_count,
            'tshirt_confirmed': shirt_count_confirmed,
            'gender': gender_count,
            'university': university_count,
            'university_confirmed': university_count_confirmed,
            'graduation_year': grad_year_count,
            'graduation_year_confirmed': grad_year_count_confirmed,
            'degree': degree_count,
            'degree_confirmed': degree_count_confirmed,
            'first_timer': first_timer_count,
            'first_timer_confirmed': first_timer_count_confirmed,
            'origin': origin_count,
            'origin_confirmed': origin_count_confirmed,
            'diet': diet_count,
            'diet_confirmed': diet_count_confirmed,
            'lennyface': lennyface_count,
            'lennyface_confirmed': lennyface_count_confirmed,
            'resume': resume_count,
            'resume_confirmed': resume_count_confirmed,
            'other_diet': '<br>'.join([el for el in other_diet])
        }
    )


@is_organizer
def users_stats_api(request):
    users = list(User.objects.all())
    users_count = defaultdict(int)
    email_verified_count = defaultdict(int)
    for u in users:
        users_count["Volunteers"] += u.is_volunteer
        users_count["Directors"] += u.is_director
        users_count["Organizers"] += u.is_organizer
        users_count["Hackers"] += not (u.is_volunteer or u.is_director or u.is_organizer)
        email_verified_count["True"] += u.email_verified
        email_verified_count["False"] += not u.email_verified

    users_count = [{'user_type': x, 'Users': v} for (x, v) in users_count.items()]

    return JsonResponse(
        {
            'update_time': timezone.now(),
            'users': users_count,
            'users_count': len(users),
            'email_verified': email_verified_count
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


class UsersStats(IsOrganizerMixin, TabsView):
    template_name = 'users_stats.html'

    def get_current_tabs(self):
        return stats_tabs()
