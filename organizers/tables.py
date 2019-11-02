import django_filters
import django_tables2 as tables
from django import forms
from django.conf import settings
from django.db.models import Q

from applications.models import Application, STATUS
from user.models import User


class ApplicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.MultipleChoiceFilter('status', label='Status', choices=STATUS,
                                                 widget=forms.CheckboxSelectMultiple)

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = Application
        fields = ['search', 'status']


class InviteFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value) |
                               Q(university__icontains=value) | Q(origin__icontains=value))

    class Meta:
        model = Application
        fields = ['search', 'first_timer', 'reimb'] if getattr(settings, 'REIMBURSEMENT_ENABLED', False) else \
            ['search', 'first_timer']


class ApplicationsListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email', 'vote_avg', 'university', 'origin']
        empty_text = 'No applications available'
        order_by = '-vote_avg'


class ApplicationTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')
    name = tables.Column(accessor='user.name', verbose_name='Full name')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        empty_text = 'No applications available'
        order_by = '-vote_avg'
        sequence = ('name', '...')


class AdminApplicationsListTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'user.name', 'vote_avg', 'reimb_amount', 'university', 'origin'] \
            if getattr(settings, 'REIMBURSEMENT_ENABLED', False) else \
            ['selected', 'user.name', 'vote_avg', 'university', 'origin']
        empty_text = 'No applications available'
        order_by = '-vote_avg'


class RankingListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['email', 'vote_count', ]
        empty_text = 'No organizers voted yet... Why? :\'('
        order_by = '-vote_count'


class AdminTeamListTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="team", verbose_name='Select')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'team', 'vote_avg', 'members']
        empty_text = 'No pending teams'
        order_by = '-vote_avg'
