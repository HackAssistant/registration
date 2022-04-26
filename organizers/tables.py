import django_filters
import django_tables2 as tables
from django import forms
from django.conf import settings
from django.db.models import Q

from applications.models import HackerApplication, STATUS, VolunteerApplication, MentorApplication, SponsorApplication
from organizers.forms import InviteFilterForm
from user.models import User


class ApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.MultipleChoiceFilter('status', label='Status', choices=STATUS,
                                                 widget=forms.CheckboxSelectMultiple)

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = HackerApplication
        fields = ['search', 'status', 'online'] if getattr(settings, 'HYBRID_HACKATHON', False) else \
            ['search', 'status']


class DubiousApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    contacted = django_filters.ChoiceFilter('contacted', label='Hacker contacted?',
                                            null_label=None,
                                            empty_label=None,
                                            choices=[(True, "Yes"), (False, "No")],
                                            widget=forms.RadioSelect)

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = HackerApplication
        fields = ['search', 'contacted']


class BlacklistApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = HackerApplication
        fields = ['search']


def get_fields_invite_filter():
    fields = ['search', 'first_timer']
    reimbursement = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
    hybrid = getattr(settings, 'HYBRID_HACKATHON', False)
    if reimbursement:
        fields.append('reimb')
    if hybrid:
        fields.append('online')
    return fields


class InviteFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = HackerApplication
        form = InviteFilterForm
        fields = get_fields_invite_filter()


def get_application_list_fields():
    fields = ['user.name', 'user.email', 'vote_avg', 'university', 'origin']
    if getattr(settings, 'HYBRID_HACKATHON', False):
        fields.append('online')
    fields.extend(['votes', 'detail'])
    return fields


class ApplicationsListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')
    votes = tables.Column(accessor='vote_set.count', verbose_name='Votes', orderable=False)

    class Meta:
        model = HackerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = get_application_list_fields()
        empty_text = 'No applications available'
        order_by = '-vote_avg'


class DubiousListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = HackerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'university', 'origin', 'contacted']
        empty_text = 'No dubious applications'
        order_by = 'status_update_date'


class BlacklistListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')

    class Meta:
        model = HackerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'university', 'origin']
        empty_text = 'No blacklisted applications'
        order_by = 'status_update_date'


def get_admin_application_list_fields():
    fields = ['selected', 'user.name', 'vote_avg']
    if getattr(settings, 'HYBRID_HACKATHON', False):
        fields.append('online')
    if getattr(settings, 'REIMBURSEMENT_ENABLED', False):
        fields.append('reimb_amount')
    fields.extend(['university', 'origin'])
    return fields


class AdminApplicationsListTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    counter = tables.TemplateColumn('{{ row_counter|add:1 }}', verbose_name='Position')
    review_count = tables.Column(accessor='vote_set.count', verbose_name='# of reviews')
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = HackerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = get_admin_application_list_fields()
        empty_text = 'No applications available'
        order_by = '-vote_avg'
        orderable = False


class AdminTeamListTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="user__team__team_code", verbose_name='Select')
    team = tables.Column(accessor='user__team__team_code')

    class Meta:
        model = HackerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'team', 'vote_avg', 'members', 'live_pending', 'invited', 'accepted']
        empty_text = 'No pending teams'
        order_by = '-vote_avg'


class VolunteerFilter(ApplicationFilter):
    class Meta:
        model = VolunteerApplication
        fields = ['search', 'status']


class VolunteerListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'volunteer_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = VolunteerApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'status']
        empty_text = 'No Volunteer Application available'
        order_by = '-submission_date'


class MentorFilter(ApplicationFilter):
    class Meta:
        model = MentorApplication
        fields = ['search', 'status']


class MentorListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'mentor_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = MentorApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'status']
        empty_text = 'No Mentor Application available'
        order_by = '-submission_date'


class SponsorFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(user__name__icontains=value) |
                               Q(name__icontains=value))

    class Meta:
        model = SponsorApplication
        fields = ['search']


class SponsorListTableWithNoAction(tables.Table):
    company = tables.Column(verbose_name='Company', accessor='user.name')

    class Meta:
        model = SponsorApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email', 'status']
        empty_text = 'No Sponsor Application available'
        order_by = '-submission_date'


class SponsorListTable(SponsorListTableWithNoAction):
    detail = tables.TemplateColumn(
        "<a href='{% url 'sponsor_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)


class SponsorUserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(name__icontains=value))

    class Meta:
        model = User
        fields = ['search']


class SponsorUserListTable(tables.Table):

    class Meta:
        model = SponsorApplication
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email', 'max_applications', 'current_applications']
        empty_text = 'No Sponsor available'
