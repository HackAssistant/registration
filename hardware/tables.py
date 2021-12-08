import django_filters
import django_tables2 as tables
from django import forms
from django.db.models import Q

from hardware.models import Request, Borrowing

REQ_CHOICES = (
    (0, 'Active'),
    (1, 'Borrowed'),
    (2, 'Expired')
)


class RequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.MultipleChoiceFilter(method='status_filter', label='Status',
                                                 choices=REQ_CHOICES, widget=forms.CheckboxSelectMultiple)

    def status_filter(self, queryset, name, value):
        if len(value) == 3 or len(value) == 0:
            return queryset.all()

        qs = queryset.none()
        if '0' in value:
            qs = qs | queryset.get_active()
        if '1' in value:
            qs = qs | queryset.get_borrowed()
        if '2' in value:
            qs = qs | queryset.get_expired()

        return qs.distinct()

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(item_type__name__icontains=value) | Q(user__name__icontains=value))

    class Meta:
        model = Request
        fields = ['search']


class BorrowingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.BooleanFilter(method='status_filter', label='Returned')

    def status_filter(self, queryset, name, value):
        if value:
            return queryset.get_returned()
        else:
            return queryset.get_active()

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(item__item_type__name__icontains=value) | Q(user__name__icontains=value))

    class Meta:
        model = Borrowing
        fields = ['search', 'status']


class RequestTable(tables.Table):
    remaining_time = tables.TemplateColumn(
        "{{record.get_remaining_time}}",
        verbose_name='Remaining time')

    class Meta:
        model = Request
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['id', 'item_type', 'user', 'borrowing', 'request_time', 'remaining_time']


class BorrowingTable(tables.Table):
    class Meta:
        model = Borrowing
        template_name = 'django_tables2/bootstrap-responsive.html'
