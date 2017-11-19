import django_filters
import django_tables2 as tables

from applications.models import Application


class ApplicationFilter(django_filters.FilterSet):
    user__email = django_filters.CharFilter('user__email', label='Email', lookup_expr='icontains')
    user__name = django_filters.CharFilter('user__name', label='Name', lookup_expr='icontains')

    class Meta:
        model = Application
        fields = ['user__email', 'user__name', 'status', 'first_timer',]


class ApplicationsListTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'app_detail' record.uuid %}' target='_blank' class='btn btn-default'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Application
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['user.name', 'vote_avg', 'user.email', 'status']
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
