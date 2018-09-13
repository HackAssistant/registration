from django.db import models
from user.models import User

BAG_ADDED = 'A'
BAG_REMOVED = 'R'

<<<<<<< HEAD
BAG_STATUS = (
    (BAG_ADDED, 'Added'),
    (BAG_REMOVED, 'Removed')
)

BAG_BUILDINGS = (
    ('A5E01', 'A5E01'),
    ('A5E02', 'A5E02')
)

=======
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
class Position(models.Model):
    """Represents a position where a baggage can be"""
    
    # Position identifier
    id = models.AutoField(primary_key=True)
    # Building identifier
<<<<<<< HEAD
    building = models.CharField(max_length=63, null=False, choices=BAG_BUILDINGS)
=======
    building = models.CharField(max_length=63, null=False)
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
    # Row identifier
    row = models.CharField(max_length=63, null=False)
    # Column identifier
    column = models.PositiveSmallIntegerField(null=False)
    # Reflects if an item is occupying this position or not
    occupied = models.BooleanField(default=False)
    
    def __str__(self):
        return self.building + '-' + self.row + str(self.column)
    
    class Meta:
        unique_together = (('building', 'row', 'column'))


class Bag(models.Model):
    """Represents a baggage item"""
    
    TYPES = (
<<<<<<< HEAD
        ('BAC', 'Backpack'),
        ('HAR', 'Hardware'),
        ('CLO', 'Clothes'),
        ('OTH', 'Other')
=======
        ('LAPTOP', 'Laptop'),
        ('OTHER', 'Other')
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
    )
    
    COLORS = (
        ('BE', 'Beige'),
        ('BK', 'Black'),
        ('BL', 'Blue'),
        ('BW', 'Brown'),
        ('CO', 'Coral'),
        ('CY', 'Cyan'),
        ('GR', 'Green'),
        ('GY', 'Grey'),
        ('LA', 'Lavender'),
        ('LI', 'Lime'),
        ('MA', 'Magenta'),
        ('MO', 'Maroon'),
        ('MI', 'Mint'),
        ('NA', 'Navy'),
        ('OL', 'Olive'),
        ('OR', 'Orange'),
        ('PI', 'Pink'),
        ('PU', 'Purple'),
        ('RE', 'Red'),
        ('TE', 'Teal'),
        ('WH', 'White'),
        ('YE', 'Yellow')
    )
    
<<<<<<< HEAD
=======
    STATUS = (
        (BAG_ADDED, 'Added'),
        (BAG_REMOVED, 'Removed')
    )
    
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
    # Item identifier
    id = models.AutoField(primary_key=True)
    # User owner of the item
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # Reflects the status of the item
<<<<<<< HEAD
    status = models.CharField(max_length=1, null=False, default=BAG_ADDED, choices=BAG_STATUS)
=======
    status = models.CharField(max_length=1, null=False, default=BAG_ADDED, choices=STATUS)
>>>>>>> 84d2bc9222f1a05e83403b71594fd431c861f98e
    # Reflects the position where the item is/was
    position = models.ForeignKey(Position, null=False, on_delete=models.PROTECT)
    # Type of item
    type = models.CharField(max_length=10, null=False, choices=TYPES)
    # Primary color of the item
    color = models.CharField(max_length=2, null=False, choices=COLORS)
    # Description of the item
    description = models.TextField(max_length=1023, null=True, blank=True)
    # Reflects if the item is special (different behaviour then) or not
    special = models.BooleanField(default=False)
    # Time for when the item was created
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    # Time for when the time was updted
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)


class Comment(models.Model):
    """Represents a comment on an item for when it was updated"""
    
    # Movement identifier
    id = models.AutoField(primary_key=True)
    # Item from which the move is related to
    item = models.ForeignKey(Bag, on_delete=models.CASCADE)
    # Time for when the comment was made
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    # User that created the movement
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # Additional comments on the movement
    comment = models.TextField(max_length=1023, null=True, blank=True)
    
    def __str__(self):
        return str(self.id)