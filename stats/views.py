from django.conf import settings
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate, TruncHour
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django_tables2 import SingleTableMixin

from app.views import TabsView
from applications.models import HackerApplication, APP_CONFIRMED, APP_ATTENDED, D_OTHER, \
    VolunteerApplication, MentorApplication, SponsorApplication, APP_DUBIOUS, APP_INVALID, APP_BLACKLISTED
from organizers.models import Vote
from stats.tables import CheckinRankingListTable, OrganizerRankingListTable
from user.mixins import is_organizer, IsOrganizerMixin
from user.models import User
from checkin.models import CheckIn

from collections import defaultdict


def stats_tabs():
    tabs = [('Hacker', reverse('app_stats'), False), ('Volunteer', reverse('volunteer_stats'), False),
            ('Mentor', reverse('mentor_stats'), False), ('Sponsor', reverse('sponsor_stats'), False),
            ('Users', reverse('users_stats'), False), ('Check-in', reverse('checkin_stats'), False),
            ('Organizers', reverse('organizer_stats'), False), ]
    if getattr(settings, 'REIMBURSEMENT_ENABLED', False):
        tabs.append(('Reimbursements', reverse('reimb_stats'), False))
    return tabs


def get_stats(model):
    hacker = model == HackerApplication
    volunteer = model == VolunteerApplication
    mentor = model == MentorApplication
    sponsor = model == SponsorApplication
    # Status analysis
    applications = list(model.objects.all())
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
    study_work_count = defaultdict(int)
    study_work_count_confirmed = defaultdict(int)
    attendance_count = defaultdict(int)
    attendance_count_confirmed = defaultdict(int)
    other_diet = []
    for a in applications:
        status_count[a.get_status_display()] += 1
        shirt_count[a.get_tshirt_size_display()] += 1
        diet_count[a.get_diet_display()] += 1
        if hacker or volunteer or mentor:
            origin_count[a.origin] += 1
            gender_count[a.get_gender_display()] += 1
        if hacker or volunteer:
            university_count[a.university] += 1
            grad_year_count[a.graduation_year] += 1
            degree_count[a.degree] += 1
            first_timer_count[a.first_timer] += 1
        if hacker:
            lennyface_count[a.lennyface] += 1
            resume_count['Resume'] += a.resume != ""
            resume_count['No resume'] += a.resume == ""
        if mentor and a.study_work:
            study_work_count['Student'] += 1
        elif mentor:
            study_work_count['Worker'] += 1
        if sponsor or volunteer or mentor:
            for day in a.get_attendance_display().split(', '):
                attendance_count[day] += 1

        if not sponsor and a.status == APP_CONFIRMED:
            shirt_count_confirmed[a.get_tshirt_size_display()] += 1
            diet_count_confirmed[a.get_diet_display()] += 1
            if hacker or volunteer or mentor:
                origin_count_confirmed[a.origin] += 1
            if hacker or volunteer:
                university_count_confirmed[a.university] += 1
                grad_year_count_confirmed[a.graduation_year] += 1
                degree_count_confirmed[a.degree] += 1
                first_timer_count_confirmed[a.first_timer] += 1
            if hacker:
                lennyface_count_confirmed[a.lennyface] += 1
                resume_count_confirmed['Resume'] += a.resume != ""
                resume_count_confirmed['No resume'] += a.resume == ""
            if mentor and a.study_work:
                study_work_count_confirmed['Student'] += 1
            elif mentor:
                study_work_count_confirmed['Worker'] += 1
            if a.diet == D_OTHER and a.other_diet:
                other_diet.append(a.other_diet)
            if volunteer or mentor:
                for day in a.get_attendance_display().split(', '):
                    attendance_count_confirmed[day] += 1

    shirt_count = [{'tshirt': x, 'applications': v} for (x, v) in shirt_count.items()]
    shirt_count_confirmed = [{'tshirt': x, 'applications': v} for (x, v) in shirt_count_confirmed.items()]

    diet_count = [{'diet': x, 'applications': v} for (x, v) in diet_count.items()]
    diet_count_confirmed = [{'diet': x, 'applications': v} for (x, v) in diet_count_confirmed.items()]

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

    lennyface_count = [{'lennyface': x, 'applications': v} for (x, v) in
                       sorted(lennyface_count.items(), key=lambda item: item[1])[-5:]]
    lennyface_count_confirmed = [{'lennyface': x, 'applications': v} for (x, v) in
                                 sorted(lennyface_count_confirmed.items(), key=lambda item: item[1])[-5:]]

    attendance_count = [{'attendance': x, 'applications': v} for (x, v) in attendance_count.items()]
    attendance_count_confirmed = [{'attendance': x, 'applications': v} for (x, v) in
                                  attendance_count_confirmed.items()]

    timeseries = model.objects.all().annotate(date=TruncDate('submission_date')).values('date').annotate(
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
            'other_diet': '<br>'.join([el for el in other_diet]),
            'study_work': study_work_count,
            'study_work_confirmed': study_work_count_confirmed,
            'attendance': attendance_count,
            'attendance_confirmed': attendance_count_confirmed,
        }
    )


@is_organizer
def reimb_stats_api(request):
    from reimbursement.models import Reimbursement, RE_STATUS, RE_DRAFT
    RE_STATUS_DICT = dict(RE_STATUS)
    # Status analysis
    status_count = Reimbursement.objects.all().values('status') \
        .annotate(reimbursements=Count('status'))
    status_count = map(lambda x: dict(status_name=RE_STATUS_DICT[x['status']], **x), status_count)

    total_apps = HackerApplication.objects.count()
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
    return get_stats(HackerApplication)


@is_organizer
def users_stats_api(request):
    users = list(User.objects.all())
    users_count = defaultdict(int)
    for u in users:
        users_count["Mentors"] += u.is_mentor()
        users_count["Sponsors"] += u.is_sponsor()
        users_count["Volunteers"] += u.is_volunteer()
        users_count["Directors"] += u.is_director
        users_count["Organizers"] += (u.is_organizer and not u.is_director)
        users_count["Hackers"] += u.is_hacker()

    users_count = [{'user_type': x, 'Users': v} for (x, v) in users_count.items()]

    return JsonResponse(
        {
            'update_time': timezone.now(),
            'users': users_count,
            'users_count': len(users),
        }
    )


def attrition_rate(application_type):
    applications = list(application_type.objects.all())
    attended = 0
    confirmed = 0
    for a in applications:
        if a.status == APP_CONFIRMED:
            confirmed += 1
        if a.status == APP_ATTENDED:
            attended += 1
    result = 0
    if confirmed or attended:
        result = attended * 100 / (confirmed + attended)
    return result


@is_organizer
def checkin_stats_api(request):
    timeseries = CheckIn.objects.all().annotate(hour=TruncHour('update_time')) \
        .values('hour').annotate(checkins=Count('hour'))
    checkin_count = len(CheckIn.objects.all())
    hacker_attrition_rate = {'Attrition rate': attrition_rate(HackerApplication)}
    volunteer_attrition_rate = {'Attrition rate': attrition_rate(VolunteerApplication)}
    mentor_attrition_rate = {'Attrition rate': attrition_rate(MentorApplication)}
    sponsor_attrition_rate = {'Attrition rate': attrition_rate(SponsorApplication)}
    return JsonResponse(
        {
            'update_time': timezone.now(),
            'timeseries': list(timeseries),
            'checkin_count': checkin_count,
            'hacker_attrition_rate': hacker_attrition_rate,
            'volunteer_attrition_rate': volunteer_attrition_rate,
            'mentor_attrition_rate': mentor_attrition_rate,
            'sponsor_attrition_rate': sponsor_attrition_rate,
        }
    )


@is_organizer
def volunteer_stats_api(request):
    return get_stats(VolunteerApplication)


@is_organizer
def mentor_stats_api(request):
    return get_stats(MentorApplication)


@is_organizer
def sponsor_stats_api(request):
    return get_stats(SponsorApplication)


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


class CheckinStats(IsOrganizerMixin, SingleTableMixin, TabsView):
    template_name = 'checkin_stats.html'
    table_class = CheckinRankingListTable

    def get_current_tabs(self):
        return stats_tabs()

    def get_queryset(self):
        return User.objects.annotate(
            checkin_count=Count('checkin')).exclude(checkin_count=0)


class VolunteerStats(IsOrganizerMixin, TabsView):
    template_name = 'volunteer_stats.html'

    def get_current_tabs(self):
        return stats_tabs()


class MentorStats(IsOrganizerMixin, TabsView):
    template_name = 'mentor_stats.html'

    def get_current_tabs(self):
        return stats_tabs()


class SponsorStats(IsOrganizerMixin, TabsView):
    template_name = 'sponsor_stats.html'

    def get_current_tabs(self):
        return stats_tabs()


class OrganizerStats(IsOrganizerMixin, SingleTableMixin, TabsView):
    template_name = 'ranking.html'
    table_class = OrganizerRankingListTable
    table_pagination = False

    def get_current_tabs(self):
        return stats_tabs()

    def get_queryset(self):
        return Vote.objects.exclude(application__status__in=[APP_DUBIOUS, APP_INVALID, APP_BLACKLISTED]) \
            .annotate(email=F('user__email')) \
            .values('email').annotate(total_count=Count('application'),
                                      skip_count=Count('application') - Count('calculated_vote'),
                                      vote_count=Count('calculated_vote')) \
            .exclude(vote_count=0)
