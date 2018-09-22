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
from baggage import utils
import base64
from django.core.files.base import ContentFile
import time


def organizer_tabs(user):
    t = [('Search', reverse('baggage_search'), False),
         ('List', reverse('baggage_list'), False)]
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
        bagimage = request.POST.get('bag_image')

        bag = Bag()
        bag.owner = User.objects.filter(id=userid).first()
        bag.type = bagtype
        bag.color = bagcolor
        bag.description = bagdesc
        bag.special = (bagspe == 'special')

        if bagimage:
            bagimageformat, bagimagefile = bagimage.split(';base64,')
            bagimageext = bagimageformat.split('/')[-1]
            bag.image = ContentFile(base64.b64decode(bagimagefile),
                                    name=(str(time.time()).split('.')[0] + '-' + userid + '.' + bagimageext))

        position = utils.get_position(bag.special)

        if position[0] != 0:
            bag.room = Room.objects.filter(room=position[1]).first()
            bag.row = position[2]
            bag.col = position[3]
            bag.save()
            messages.success(self.request, 'Bag checked-in!')
            return redirect('baggage_detail', id=(str(bag.id,)), first='first/')
        messages.success(self.request, 'Error! Couldn\'t add the bag!')
        return redirect('baggage_list')


class BaggageDetail(TabsView):
    template_name = 'baggage_detail.html'

    def get_back_url(self):
        if self.kwargs['first'] != 'first/':
            return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(BaggageDetail, self).get_context_data(**kwargs)
        bagid = kwargs['id']
        bagfirst = (kwargs['first'] == 'first/')
        bag = Bag.objects.filter(id=bagid).first()
        if not bag:
            raise Http404
        context.update({
            'bag': bag,
            'position': bag.position(),
            'checkedout': bag.status == BAG_REMOVED,
            'first': bagfirst
        })
        return context

    def post(self, request, *args, **kwargs):
        bagid = request.POST.get('bag_id')
        bag = Bag.objects.filter(id=bagid).first()
        bag.status = BAG_REMOVED
        bag.save()
        messages.success(self.request, 'Bag checked-out!')
        return redirect('baggage_list')
