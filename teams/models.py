import random

from django.db import models

from user.models import User

TEAM_ID_LENGTH = 13


def generate_team_id():
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    passlen = TEAM_ID_LENGTH
    return "".join(random.sample(s, passlen))


class Team(models.Model):
    team_code = models.CharField(default=generate_team_id, max_length=TEAM_ID_LENGTH)
    user = models.OneToOneField(User)

    class Meta:
        unique_together = (("team_code", "user"),)
