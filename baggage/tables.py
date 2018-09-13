import django_filters
import django_tables2 as tables
<<<<<<< HEAD
from baggage.models import Bag, BAG_STATUS, BAG_ADDED, BAG_BUILDINGS
from django.db.models import Q
from django import forms

class BaggageListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    status = django_filters.ChoiceFilter('status', label='Status', choices=BAG_STATUS,
                                                 widget=forms.RadioSelect, empty_label='Any', initial=BAG_ADDED)
    position__building = django_filters.ChoiceFilter(label='Building', choices=BAG_BUILDINGS, empty_label='Any')
    time_from = django_filters.DateTimeFilter(method='search_time', label='Time from', widget=forms.DateTimeInput(attrs={'class': 'field-left'}))
    time_to = django_filters.DateTimeFilter(method='search_time', label='Time to', widget=forms.DateTimeInput(attrs={'class': 'field-right'}))

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(owner__email__icontains=value) | Q(owner__name__icontains=value) |
            Q(status__icontains=value) | Q(type__icontains=value) | Q(color__icontains=value) | Q(description__icontains=value) |
            Q(position__building__icontains=value)))

    def search_time(self, queryset, name, value):
        if name == 'time_from':
            return queryset.filter(Q(time__gte=value))
        return queryset.filter(Q(time__lte=value))
=======
from baggage.models import Bag
from django.db.models import Q

class BaggageListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(owner__email__icontains=value) | Q(owner__name__icontains=value) |
            Q(status__icontains=value) | Q(type__icontains=value) | Q(color__icontains=value) | Q(description__icontains=value))
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e

    class Meta:
        model = Bag
        fields = ['search']

class BaggageListTable(tables.Table):
<<<<<<< HEAD
    class Meta:
        model = Bag
        attrs = {'class': 'table table-hover'}
        template = 'templates/baggage_list.html'
        fields = ['id', 'position.building', 'position.row', 'position.column', 'owner', 'type', 'description', 'special']
=======

    class Meta:
        model = Bag
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['id', 'owner', 'type', 'description', 'special']
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
        empty_text = 'No baggage items checked-in'