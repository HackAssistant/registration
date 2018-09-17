from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    description = models.CharField(max_length=2000)
    video = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    desired_prizes = models.CharField(max_length=400)
    built_with = models.CharField(blank=True, null=True, max_length=400)
    submitter_screen_name = models.CharField(blank=True, null=True, max_length=200)
    submitter_first_name = models.CharField(blank=True, null=True, max_length=100)
    submitter_last_name = models.CharField(blank=True, null=True, max_length=100)
    submitter_email = models.CharField(blank=True, null=True, max_length=200)
    university = models.CharField(blank=True, null=True, max_length=300)
    additional_team_member_count = models.IntegerField(default=0)


class Challenge(models.Model):
    name = models.CharField(max_length=25)


class Room(models.Model):
    name = models.CharField(max_length=15)
    challenge = models.ForeignKey(Challenge, on_delete=None)


class Presentation(models.Model):
    project = models.ForeignKey(Project, on_delete=None)
    room = models.ForeignKey(Room, on_delete=None)
