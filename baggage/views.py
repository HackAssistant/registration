from django.core.urlresolvers import reverse
from app.mixins import TabsViewMixin
from baggage.tables import BaggageListTable, BaggageListFilter, BaggageUsersTable, BaggageUsersFilter
from baggage.models import Bag, BAG_ADDED, BAG_REMOVED, Room
from user.models import User
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from app.views import TabsView
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
import math
import itertools

def organizer_tabs(user):
    t = [('Search', reverse('baggage_search'), False),
         ('List', reverse('baggage_list'), False)]
    return t

class BaggageList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    filterset_class = BaggageListFilter
    table_pagination = {'per_page': 100}
    
    def calculate_distance(self, ini_x, ini_y, end_x, end_y):
        return ((end_x, end_y), math.sqrt(pow(abs(end_x-ini_x), 2)+pow(abs(end_y-ini_y), 2)))

    def nearest_available(x, y):
        rooms = Room.objects.all()
        positions = []
        for room in rooms:
            positions.insert(list(0, room.row))
        print(str(positions))
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        rooms = Room.objects.all()
        positions = list(itertools.product(list(map(str, range(0, 10))), list(map(str, range(0, 13)))))
        positions_dist = list(map(lambda x : calculate_distance(0, 0, int(x[0]), int(x[1])), positions))
        positions_sort = sorted(positions_dist, key=(lambda x : x[1]))
        print(positions)
        return Bag.objects.filter(status=BAG_ADDED)

class BaggageUsers(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'baggage_users.html'
    table_class = BaggageUsersTable
    filterset_class = BaggageUsersFilter
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return User.objects.filter(email_verified=True)

class BaggageAdd(TabsView):
    template_name = 'baggage_add.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(BaggageAdd, self).get_context_data(**kwargs)
        userid = kwargs['new_id']
        user = User.objects.filter(id=userid).first()
        if not user:
            raise Http404
        context.update({
            'user': user
        })
        return context

    def post(self, request, *args, **kwargs):
        bagtype = request.POST.get('bag_type')
        bagcolor = request.POST.get('bag_color')
        bagdesc = request.POST.get('bag_description')
        bagspe = request.POST.get('bag_special')
        userid = request.POST.get('user_id')
        bag = Bag()
        bag.owner = User.objects.filter(id=userid).first()
        bag.type = bagtype
        bag.color = bagcolor
        bag.description = bagdesc
        bag.special = (bagspe == 'special')
        bag.room = Room.objects.all().first()
        bag.row = 'A'
        bag.col = 0
        bag.save()
        messages.success(self.request, 'Bag checked-in!')
        return redirect('baggage_detail', id=(str(bag.id,)), first='first/')

class BaggageDetail(TabsView):
    template_name = 'baggage_detail.html'

    def get_back_url(self):
        if self.kwargs['first'] != 'first/':
            return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(BaggageDetail, self).get_context_data(**kwargs)
        bagid = kwargs['id']
        bagfirst = kwargs['first']
        bag = Bag.objects.filter(id=bagid).first()
        if not bag:
            raise Http404
        context.update({
            'bag': bag,
            'position': bag.position(),
            'checkedout': bag.status == BAG_REMOVED,
            'first' : bagfirst
        })
        return context

    def post(self, request, *args, **kwargs):
        bagid = request.POST.get('bag_id')
        bag = Bag.objects.filter(id=bagid).first()
        bag.status = BAG_REMOVED
        bag.save()
        messages.success(self.request, 'Bag checked-out!')
        return redirect('baggage_list')