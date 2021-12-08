from app import hackathon_variables
from app.mixins import TabsViewMixin
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.db.models import Q
from user.mixins import IsHardwareAdminMixin, IsHackerMixin
from user.models import User
from checkin.models import CheckIn

from hardware.models import Item, ItemType, Borrowing, Request
from hardware.tables import BorrowingTable, BorrowingFilter, RequestTable, RequestFilter


def hardware_tabs(user):
    if user.is_hardware_admin or user.is_organizer:
        return [
            ('Hardware Admin', reverse('hw_admin'), False),
            ('Requests', reverse('hw_requests'), False),
            ('Borrowings', reverse('hw_borrowings'), False)
        ]
    else:
        return [
            ('Hardware List', reverse('hw_list'), False),
            ('Borrowings', reverse('hw_borrowings'), False)
        ]


class HardwareAdminRequestsView(TabsViewMixin, IsHardwareAdminMixin,
                                SingleTableMixin, FilterView):
    template_name = 'hardware_requests.html'
    table_class = RequestTable
    table_pagination = {'per_page': 50}
    filterset_class = RequestFilter

    def get_current_tabs(self):
        return hardware_tabs(self.request.user)

    def get_queryset(self):
        return Request.objects.all()


class HardwareBorrowingsView(IsHackerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'hardware_borrowings.html'
    table_class = BorrowingTable
    table_pagination = {'per_page': 50}
    filterset_class = BorrowingFilter

    def get_context_data(self, **kwargs):
        context = super(HardwareBorrowingsView, self).get_context_data(**kwargs)
        if not self.request.user.is_hardware_admin:
            context['filter'] = False
            context['table'].exclude = ('id', 'user', 'lending_by', 'return_by')

        return context

    def get_current_tabs(self):
        return hardware_tabs(self.request.user)

    def get_queryset(self):
        if self.request.user.is_hardware_admin:
            return Borrowing.objects.all()
        else:
            return Borrowing.objects.get_queryset().filter(user=self.request.user)


class HardwareListView(IsHackerMixin, TabsViewMixin, TemplateView):
    template_name = 'hardware_list.html'

    def get_current_tabs(self):
        return hardware_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HardwareListView, self).get_context_data(**kwargs)
        context['hw_list'] = ItemType.objects.all()
        requests = Request.objects.get_active_by_user(self.request.user)
        context['requests'] = {
            x.item_type.id: x.get_remaining_time() for x in requests
        }
        return context

    def req_item(self, request):
        item = ItemType.objects.get(id=request.POST['item_id'])
        if item.get_available_count() > 0:
            item.make_request(request.user)
            return JsonResponse({
                'ok': True,
                'minutes': hackathon_variables.HARDWARE_REQUEST_TIME
            })

        return JsonResponse({'msg': "ERROR: There are no items available"})

    def check_availability(self, request):
        item_ids = request.POST['item_ids[]']
        items = ItemType.objects.filter(id__in=item_ids)
        available_items = []
        for item in items:
            if item.get_available_count() > 0:
                available_items.append({
                    "id": item.id,
                    "name": item.name
                })

        return JsonResponse({
            'available_items': available_items
        })

    def post(self, request):
        if request.is_ajax:
            if 'req_item' in request.POST:
                return self.req_item(request)
            if 'check_availability' in request.POST:
                return self.check_availability(request)


class HardwareAdminView(IsHardwareAdminMixin, TabsViewMixin, TemplateView):
    template_name = 'hardware_admin.html'

    def init_and_toast(self, msg):
        """
        Finishes a process and goes back to the beginning while
        showing a toast
        """
        html = render_to_string("include/hardware_admin_init.html", {
            'hw_list': ItemType.objects.all(),
        })
        return JsonResponse({
            'content': html,
            'msg': msg
        })

    def get_lists(self, request):
        """
        When a user has a request or a borrowing we get the lists
        to proceed
        """
        target_user = User.objects.filter(email=request.POST['email'])
        if not target_user.exists():
            # In this case we don't want to return to the initial page
            return JsonResponse({
                'msg': "ERROR: The user doesn't exist"
            })

        requests = Request.objects.get_active_by_user(target_user.first())
        borrowings = Borrowing.objects.get_active_by_user(target_user.first())
        html = render_to_string("include/hardware_admin_user.html", {
            'requests': requests,
            'borrowings': borrowings
        })
        return JsonResponse({
            'content': html
        })

    def select_request(self, request):
        """
        We selected a request to process a borrowing. Then we show a list
        with the available items of that type
        """
        request_obj = Request.objects.get(id=request.POST['request_id'])
        if not request_obj.is_active():
            return self.init_and_toast("ERROR: The request has expired")

        available_items = request_obj.item_type.get_borrowable_items()
        html = render_to_string("include/hardware_admin_borrowing.html", {
            'items': available_items,
            'request_id': request.POST['request_id']
        })
        return JsonResponse({'content': html})

    def return_item(self, request):
        """
        We selected a borrowing to end it
        """
        borrowing = Borrowing.objects.get(id=request.POST['borrowing_id'])
        if not borrowing.is_active():
            return self.init_and_toast("ERROR: The item was not borrowed")

        borrowing.return_time = timezone.now()
        borrowing.return_by = request.user
        borrowing.save()
        return self.init_and_toast("The item has been returned succesfully")

    def make_borrowing(self, request):
        """
        Once we choose the item, we can now make the borrowing
        and finish the process
        """
        item = Item.objects.get(id=request.POST['item_id'])
        if not item.can_be_borrowed():
            return self.init_and_toast("ERROR: The item is not available")

        request_obj = Request.objects.get(id=request.POST['request_id'])
        borrowing = Borrowing(user=request_obj.user, item=item, borrowing_by=request.user)
        borrowing.save()
        request_obj.borrowing = borrowing
        request_obj.save()
        return self.init_and_toast("The item has been borrowed succesfully")

    def select_type_noreq(self, request):
        """
        When a hacker doesn't have a request, we first select the hardware
        """
        item_type = ItemType.objects.get(id=request.POST['type_id'])
        if item_type.get_available_count() <= 0:
            return self.init_and_toast("ERROR: There are no items available")

        available_items = item_type.get_borrowable_items()
        html = render_to_string("include/hardware_admin_borrowing.html", {
            'items': available_items,
        })
        return JsonResponse({'content': html})

    def select_item_noreq(self, request):
        """
        We selected an item without request. We still need a user
        """
        item = Item.objects.get(id=request.POST['item_id'])
        if not item.can_be_borrowed():
            return self.init_and_toast("ERROR: The item is not available")

        html = render_to_string("include/hardware_user_email.html", {
            'item_id': item.id
        })
        return JsonResponse({
            'content': html
        })

    def get_user_noreq(self, request):
        """
        We can make the borrowing without request now
        """
        item = Item.objects.get(id=request.POST['item_id'])
        target_user = User.objects.filter(email=request.POST['email'])
        if not target_user.exists():
            # In this case we don't want to return to the initial page
            return JsonResponse({
                'msg': "ERROR: The user doesn't exist"
            })
        if not item.can_be_borrowed():
            return self.init_and_toast("ERROR: The item is not available")

        borrowing = Borrowing(user=target_user.first(), item=item, borrowing_by=request.user)
        borrowing.save()
        return self.init_and_toast("The item has been borrowed succesfully")

    def identify_hacker(self, request):
        """
        Gets a list of suggestions based on the input (typeahead)
        """
        checkins = CheckIn.objects.filter(
            Q(hacker__user__name__icontains=request.POST['query']) |
            Q(hacker__user__email__startswith=request.POST['query']) |
            Q(qr_identifier=request.POST['query']))

        users = [x.application.user for x in checkins]

        return HttpResponse(serializers.serialize('json', list(users), fields=('name', 'email')))

    def post(self, request):
        if request.is_ajax:
            if 'identify_hacker' in request.POST:
                return self.identify_hacker(request)
            if 'get_lists' in request.POST:
                return self.get_lists(request)
            if 'select_request' in request.POST:
                return self.select_request(request)
            if 'return_item' in request.POST:
                return self.return_item(request)
            if 'make_borrowing' in request.POST:
                return self.make_borrowing(request)
            if 'select_type_noreq' in request.POST:
                return self.select_type_noreq(request)
            if 'select_item_noreq' in request.POST:
                return self.select_item_noreq(request)
            if 'get_user_noreq' in request.POST:
                return self.get_user_noreq(request)
            if 'back' in request.POST:
                return self.init_and_toast("")

    def get_current_tabs(self):
        return hardware_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HardwareAdminView, self).get_context_data(**kwargs)
        context['hw_list'] = ItemType.objects.all()
        return context
