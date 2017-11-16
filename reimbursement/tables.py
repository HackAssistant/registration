import django_filters
import django_tables2 as tables

from reimbursement.models import Reimbursement


class ReimbursementFilter(django_filters.FilterSet):
    hacker__email = django_filters.CharFilter('hacker__email', label='Email', lookup_expr='icontains')
    hacker__nickname = django_filters.CharFilter('hacker__nickname', label='Preferred name', lookup_expr='icontains')
    origin_city = django_filters.CharFilter('origin_city', label='Origin city', lookup_expr='icontains')
    origin_country = django_filters.CharFilter('origin_country', label='Origin country', lookup_expr='icontains')

    class Meta:
        model = Reimbursement
        fields = ['hacker__email', 'hacker__nickname', 'origin_country', 'origin_city', 'status']


class ReimbursementTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'reimbursement_detail' record.pk %}' class='btn btn-default'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Reimbursement
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['hacker.nickname', 'hacker.email', 'assigned_money', 'reimbursement_money', 'status', 'origin_city',
                  'origin_country', ]

        empty_text = 'No reimbursement match criteria'
