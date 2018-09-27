from django.db import models
from user.models import User

MEAL_TYPE = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner'),
    ('S', 'Snack'),
    ('O', 'Other')
)


class Meal(models.Model):
    """Represents a meal that the hacker can eat"""

    # Meal name
    name = models.CharField(max_length=63, null=False)
    # Meal type
    kind = models.CharField(max_length=63, null=False, choices=MEAL_TYPE)
    # Starting time
    starts = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    # Ending time
    ends = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    # Number of times a hacker can eat this meal
    times = models.PositiveIntegerField(null=False, default=1)

    def __str__(self):
        return str(self.name)

    def eaten(self):
        return Eaten.objects.filter(meal=self).count()


class Eaten(models.Model):
    """Represents when a hacker has eatean a meal"""

    # Meal that was eaten
    meal = models.ForeignKey(Meal, null=False, on_delete=models.CASCADE)
    # User that ate the meal
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # Ate time
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
