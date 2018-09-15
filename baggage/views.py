from django.core.urlresolvers import reverse
from app.mixins import TabsViewMixin
from baggage.tables import BaggageListTable, BaggageListFilter
from baggage.models import Bag, BAG_ADDED
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from datetime import timedelta
from django.utils import timezone

def organizer_tabs(user):
    t = [('Overview', reverse('baggage_list'), False),
         ('Check-in', reverse('baggage_add'), False),
         ('Check-out', reverse('baggage_del'), False)]
    return t

class BaggageList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Bag.objects.filter(status=BAG_ADDED).filter(time__lte=timezone.now()).filter(time__gte=timezone.now()-timedelta(1))

class BaggageAdd(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Bag.objects.filter(status=BAG_ADDED).filter(time__lte=timezone.now()).filter(time__gte=timezone.now()-timedelta(1))

class BaggageDel(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Bag.objects.filter(status=BAG_ADDED).filter(time__lte=timezone.now()).filter(time__gte=timezone.now()-timedelta(1))