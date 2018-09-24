from django.db import models
from user.models import User
from django.utils.datetime_safe import datetime


class Meal(models.Model):
    """Represents a meal that the hacker can eat"""

    # Meal name
    room = models.CharField(max_length=63, null=False)
    # Starting time
    starts = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    # Ending time
    ends = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)


class Eaten(models.Model):
    """Represents when a hacker has eatean a meal"""

    # Meal that was eaten
    meal = models.ForeignKey(Meal, null=False, on_delete=models.CASCADE)
    # User that ate the meal
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # Times the user has eaten the same meal
    times = models.PositiveIntegerField(null=False, default=1)
