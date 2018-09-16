from django.core.urlresolvers import reverse
from app.mixins import TabsViewMixin
from baggage.tables import BaggageListTable, BaggageListFilter
from baggage.models import Bag, BAG_ADDED, BAG_REMOVED
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from app.views import TabsView
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect

def organizer_tabs(user):
    t = [('Check-in', reverse('baggage_add'), False),
         ('Check-out', reverse('baggage_list'), False)]
    return t

class BaggageList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Bag.objects.filter(status=BAG_ADDED)

class BaggageAdd(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Bag.objects.filter(status=BAG_ADDED)

class BaggageDetail(TabsView):
    template_name = 'baggage_detail.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(BaggageDetail, self).get_context_data(**kwargs)
        bagid = kwargs['id']
        bag = Bag.objects.filter(id=bagid).first()
        if not bag:
            raise Http404
        context.update({
            'bag': bag,
            'checkedout': bag.status == BAG_REMOVED
        })
        return context

    def post(self, request, *args, **kwargs):
        bagid = request.POST.get('bag_id')
        bag = Bag.objects.filter(id=bagid).first()
        bag.status = BAG_REMOVED
        bag.save()
        messages.success(self.request, 'Bag checked-out!')
        return redirect('baggage_list')