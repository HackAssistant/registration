import django_filters
import django_tables2 as tables
from django import forms
from django.db.models import Q

from reimbursement.models import Reimbursement, RE_STATUS


class ReimbursementFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.MultipleChoiceFilter('status', label='Status', choices=RE_STATUS,
                                                 widget=forms.CheckboxSelectMultiple)

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(hacker__email__icontains=value) | Q(hacker__name__icontains=value) | Q(origin__icontains=value)
        )

    class Meta:
        model = Reimbursement
        fields = ['search', 'status']


class ReimbursementTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'reimbursement_detail' record.pk %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)

    class Meta:
        model = Reimbursement
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['hacker.name', 'hacker.email', 'assigned_money', 'reimbursement_money', 'status', 'origin', ]

        empty_text = 'No reimbursement match criteria'


class SendReimbursementFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(hacker__email__icontains=value) | Q(hacker__name__icontains=value) | Q(origin__icontains=value)
        )

    class Meta:
        model = Reimbursement
        fields = ['search', ]


class SendReimbursementTable(tables.Table):
    detail = tables.TemplateColumn(
        "<a href='{% url 'reimbursement_detail' record.pk %}' target='_blank'>Open</a> ",
        verbose_name='Actions', orderable=False)

    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    assigned_money = tables.TemplateColumn(
        "<input type='number' min='0' name='am_{{record.pk}}' value='{{record.assigned_money}}'/> ",
        verbose_name='Assigned money', orderable=False)

    class Meta:
        model = Reimbursement
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'assigned_money', 'hacker.email', 'origin', ]

        empty_text = 'No reimbursement match criteria'
