from django.db import models

from user.models import User


class DiscordUser(models.Model):
    user = models.OneToOneField(to=User, unique=True)
    discord_id = models.CharField(max_length=50, primary_key=True)
    discord_username = models.CharField(max_length=100, null=True)
    checked_in = models.BooleanField(default=False)
    team_name = models.CharField(max_length=100, blank=True)
    swag = models.BooleanField(default=False)
    address = models.CharField(max_length=1000, blank=True, default='')
    stickers = models.CharField(max_length=500, blank=True, default='')
    pick_up = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
