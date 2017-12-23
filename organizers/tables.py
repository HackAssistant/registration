import django_filters
import django_tables2 as tables

from applications.models import Application
from user.models import User


class ApplicationFilter(django_filters.FilterSet):
    user__email = django_filters.CharFilter('user__email', label='Email', lookup_expr='icontains')
    user__name = django_filters.CharFilter('user__name', label='Name', lookup_expr='icontains')
    university = django_filters.CharFilter('university', label='University', lookup_expr='icontains')

    class Meta:
        model = Application
        fields = ['user__email', 'user__name', 'status', 'first_timer', 'university']


class ApplicationsListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    origin = tables.Column(accessor='origin', verbose_name='Origin')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'vote_avg', 'user.email', 'status', 'university', 'origin']
        empty_text = 'No applications available'
        order_by = '-vote_avg'


class AdminApplicationsListTable(ApplicationsListTable):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'user.name', 'vote_avg', 'user.email', 'status']
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
