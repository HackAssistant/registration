from django.db import models

from user.models import User


class DiscordUser(models.Model):
    user = models.OneToOneField(to=User, unique=True)
    discord_id = models.CharField(max_length=50, primary_key=True)
    discord_username = models.CharField(max_length=100, null=True)
    checked_in = models.BooleanField(default=False)
    team_name = models.CharField(max_length=100, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.team_name is None and hasattr(self.user, 'team'):
            self.team_name = self.user.team.team_code
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.user.email
