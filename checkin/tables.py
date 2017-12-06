import django_filters
import django_tables2 as tables

from applications.models import Application
from user.models import User


class ApplicationCheckinFilter(django_filters.FilterSet):
    user__email = django_filters.CharFilter('user__email', label='Email', lookup_expr='icontains')
    user__name = django_filters.CharFilter('user__name', label='Preferred name', lookup_expr='icontains')

    class Meta:
        model = Application
        fields = ['user__email', 'user__name']


class ApplicationsCheckInTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'check_in_hacker' record.uuid %}'>Check-in</a> ",
        verbose_name='Actions', )

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'user.email']
        empty_text = 'All hackers checked in! Yay!'

class RankingListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['email', 'checkin_count', ]
        empty_text = 'No checked in hacker yet... Why? :\'('
        order_by = '-checkin_count'
