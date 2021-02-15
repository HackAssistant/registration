from django.db import models

from user.models import User


class DiscordUser(models.Model):
    user = models.OneToOneField(to=User, primary_key=True)
    discord_id = models.CharField(max_length=50, unique=True)
    checked_in = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
