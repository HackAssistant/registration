import django_filters
import django_tables2 as tables
from django.db.models import Q

from user.models import User


class ApplicationCheckinFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(name__icontains=value) |
                               Q(id__icontains=value.replace('-', '')))

    class Meta:
        model = User
        fields = ['search']


class ApplicationsCheckInTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'check_in_hacker' id=record.id %}'>Check-in</a> ",
        verbose_name='Actions', )

    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email']
        empty_text = 'No hacker found, have they all checked-in??'


class RankingListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['email', 'checkin_count', ]
        empty_text = 'No checked in hacker yet... Why? :\'('
        order_by = '-checkin_count'
