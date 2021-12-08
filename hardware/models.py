from datetime import timedelta

from app import hackathon_variables
from django.db import models
from django.utils import timezone
from user.models import User


class ItemType(models.Model):
    """Represents a kind of hardware"""

    # Human readable name
    name = models.CharField(max_length=50, unique=True)
    # Image of the hardware
    image = models.FileField(upload_to='hw_images/')
    # Description of this hardware
    # what is it used for? which items are contained in the package?
    description = models.TextField()

    def get_borrowable_items(self):
        """ Get items not borrowed already """
        availables = Item.objects.filter(item_type=self, available=True)
        borrowings = Borrowing.objects.filter(item__item_type=self, return_time__isnull=True)
        return availables.exclude(id__in=[x.item.id for x in borrowings])

    def get_available_count(self):
        ava_count = Item.objects.filter(item_type=self, available=True).count()
        req_count = self.get_requested_count()
        borrowed_count = self.get_borrowed_count()
        return ava_count - req_count - borrowed_count

    def get_requested_count(self):
        return Request.objects.get_active_by_item_type(self).count()

    def get_borrowed_count(self):
        return Borrowing.objects.get_active_by_item_type(self).count()

    def get_unavailable_count(self):
        return Item.objects.filter(item_type=self, available=False).count()

    def make_request(self, user):
        req = Request(item_type=self, user=user)
        req.save()

    def __str__(self):
        return self.name


class Item(models.Model):
    """Represents a real world object identified by label"""

    # Hardware model/type
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    # Identifies a real world object
    label = models.CharField(max_length=20, unique=True)
    # Is the item available?
    available = models.BooleanField(default=True)
    # Any other relevant information about this item
    comments = models.TextField(blank=True, null=True)

    def can_be_borrowed(self):
        return Borrowing.objects.filter(return_time__isnull=True, item=self).count() == 0

    def __str__(self):
        return '{} ({})'.format(self.label, self.item_type.name)


class BorrowingQuerySet(models.QuerySet):
    def get_active(self):
        return self.filter(return_time__isnull=True)

    def get_returned(self):
        return self.filter(return_time__isnull=False)

    def get_active_by_item_type(self, item_type):
        return self.filter(return_time__isnull=True, item__item_type=item_type)

    def get_active_by_user(self, user):
        return self.filter(return_time__isnull=True, user=user)


class Borrowing(models.Model):
    """
    The 'item' has been borrowed to the 'user'
    """
    objects = BorrowingQuerySet.as_manager()

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    # Instant of creation
    picked_up_time = models.DateTimeField(auto_now_add=True)
    # If null: item has not been returned yet
    return_time = models.DateTimeField(null=True, blank=True)

    # Borrowing handled by
    borrowing_by = models.ForeignKey(User, related_name='hardware_admin_borrowing', on_delete=models.DO_NOTHING)
    # Return handled by (null until returned)
    return_by = models.ForeignKey(User, related_name='hardware_admin_return', null=True, blank=True,
                                  on_delete=models.SET_NULL)

    def get_picked_up_time_ago(self):
        return str(timezone.now() - self.picked_up_time)

    def get_return_time_ago(self):
        return str(timezone.now() - self.return_time)

    def is_active(self):
        return self.return_time is None

    def __str__(self):
        return '{} ({})'.format(self.item.item_type.name, self.user)


class RequestQuerySet(models.QuerySet):
    def get_active(self):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        threshold = timezone.now() - delta
        return self.filter(borrowing__isnull=True, request_time__gte=threshold)

    def get_borrowed(self):
        return self.filter(borrowing__isnull=False)

    def get_expired(self):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        threshold = timezone.now() - delta
        return self.filter(borrowing__isnull=True, request_time__lt=threshold)

    def get_active_by_user(self, user):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        threshold = timezone.now() - delta
        return self.filter(borrowing__isnull=True, request_time__gte=threshold, user=user)

    def get_active_by_item_type(self, item_type):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        threshold = timezone.now() - delta
        return self.filter(borrowing__isnull=True, request_time__gte=threshold, item_type=item_type)


class Request(models.Model):
    """
    Represents reservation of an item
    of type 'item_type' done by 'user'
    """

    objects = RequestQuerySet.as_manager()

    # Requested item type
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    # Hacker that made the request
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Borrowing derived from this request
    borrowing = models.ForeignKey(Borrowing, null=True, blank=True, on_delete=models.CASCADE)
    # Instant of creation
    request_time = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        remaining = delta - (timezone.now() - self.request_time)
        return not self.borrowing and remaining.total_seconds() > 0

    def get_remaining_time(self):
        delta = timedelta(minutes=hackathon_variables.HARDWARE_REQUEST_TIME)
        remaining = delta - (timezone.now() - self.request_time)
        if self.borrowing:
            return "Borrowed"
        elif remaining.total_seconds() < 0:
            return "Expired"
        else:
            return str(remaining)

    def __str__(self):
        return '{} ({})'.format(self.item_type, self.user)
