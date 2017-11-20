import django_filters
import django_tables2 as tables

from reimbursement.models import Reimbursement


class ReimbursementFilter(django_filters.FilterSet):
    hacker__email = django_filters.CharFilter('hacker__email', label='Email', lookup_expr='icontains')
    hacker__name = django_filters.CharFilter('hacker__name', label='Name', lookup_expr='icontains')
    origin_city = django_filters.CharFilter('origin_city', label='City', lookup_expr='icontains')
    origin_country = django_filters.CharFilter('origin_country', label='Country', lookup_expr='icontains')

    class Meta:
        model = Reimbursement
        fields = ['hacker__email', 'hacker__name', 'origin_country', 'origin_city', 'status']


class ReimbursementTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'reimbursement_detail' record.pk %}' class='btn btn-default'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Reimbursement
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['hacker.name', 'hacker.email', 'assigned_money', 'reimbursement_money', 'status', 'origin_city',
                  'origin_country', ]

        empty_text = 'No reimbursement match criteria'


class SendReimbursementFilter(django_filters.FilterSet):
    hacker__email = django_filters.CharFilter('hacker__email', label='Email', lookup_expr='icontains')
    hacker__name = django_filters.CharFilter('hacker__name', label='Name', lookup_expr='icontains')
    origin_city = django_filters.CharFilter('origin_city', label='City', lookup_expr='icontains')
    origin_country = django_filters.CharFilter('origin_country', label='Country', lookup_expr='icontains')

    class Meta:
        model = Reimbursement
        fields = ['hacker__email', 'hacker__name', 'origin_country', 'origin_city', ]


class SendReimbursementTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'reimbursement_detail' record.pk %}' target='_blank' class='btn btn-default'>Open</a> ",
        verbose_name='Actions', orderable=False)

    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    assigned_money = tables.TemplateColumn(
        "<input type='number' min='0' name='am_{{record.pk}}' value='{{record.assigned_money}}'/> ",
        verbose_name='Assigned money', orderable=False)

    class Meta:
        model = Reimbursement
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'assigned_money', 'hacker.email', 'origin_city',
                  'origin_country', ]

        empty_text = 'No reimbursement match criteria'
