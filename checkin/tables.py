import django_filters
import django_tables2 as tables

from applications.models import Application


class ApplicationCheckinFilter(django_filters.FilterSet):
    user__email = django_filters.CharFilter('user__email', label='Email', lookup_expr='icontains')
    user__nickname = django_filters.CharFilter('user__nickname', label='Preferred name', lookup_expr='icontains')

    class Meta:
        model = Application
        fields = ['user__email', 'user__nickname']


class ApplicationsCheckInTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'check_in_hacker' record.uuid %}' class='btn btn-success'>Check-in</a> ",
        verbose_name='Actions', )

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.nickname', 'user.email']
        empty_text = 'No applications available'
