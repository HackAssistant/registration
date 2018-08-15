import django_filters
import django_tables2 as tables
from baggage.models import Bag, BAG_STATUS, BAG_ADDED
from django.db.models import Q
from django import forms

class BaggageListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.ChoiceFilter('status', label='Status', choices=BAG_STATUS,
                                                 widget=forms.RadioSelect, empty_label=None, initial=BAG_ADDED)
    time = django_filters.TypedChoiceFilter('time', label='Time', widget=forms.DateField)

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(owner__email__icontains=value) | Q(owner__name__icontains=value) |
            Q(status__icontains=value) | Q(type__icontains=value) | Q(color__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = Bag
        fields = ['search']

class BaggageListTable(tables.Table):

    class Meta:
        model = Bag
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['id', 'owner', 'type', 'description', 'special']
        empty_text = 'No baggage items checked-in'