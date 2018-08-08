from django.db import models
from user.models import User

class Item(models.Model):
    """Represents a baggage item"""
    
    TYPES = (
        ('LAPTOP', 'Laptop'),
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
    
    # Item identifier
    id = models.AutoField(primary_key=True)
    # User owner of the item
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # Reflects if the item is under our surveillance or not
    active = models.BooleanField(default=True)
    # Type of item
    type = models.CharField(max_length=10, null=False, choices=TYPES)
    # Primary color of the item
    color = models.CharField(max_length=2, null=False, choices=COLORS)
    # Description of the item
    description = models.TextField(max_length=1023, null=True, blank=True)
    # Reflects if the item is special (different behaviour then) or not
    special = models.BooleanField(default=False)


class Position(models.Model):
    """Represents a position where a baggage can be"""
    
    # Building identifier
    building = models.CharField(max_length=63, null=False)
    # Row identifier
    row = models.CharField(max_length=63, null=False)
    # Column identifier
    column = models.PositiveSmallIntegerField(null=False)
    # Current item occupying this position
    content = models.ForeignKey(Item, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        unique_together = (('building', 'row', 'column'))


class Movement(models.Model):
    """Represents a movement of an item in a position"""
    
    TYPES = (
        ('ADD', 'Added'),
        ('MOD', 'Modified'),
        ('DEL', 'Removed')
    )
    
    # Movement identifier
    id = models.AutoField(primary_key=True)
    # Item from which the move is related to
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    # Position where the item is/was
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    # Time for when the movement was made
    time = models.DateField(auto_now=False, auto_now_add=True)
    # User that created the movement
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # Type of the movement
    type = models.CharField(max_length=3, null=False)
    # Additional comments on the movement
    comment = models.TextField(max_length=1023, null=True, blank=True)
    # Reflects if a receipt was printed
    receipt = models.BooleanField(default=False)