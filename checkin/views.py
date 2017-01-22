from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from django.db import models

# Create your views here.
from django.views.generic import TemplateView
from models import CheckIn
from register.models import Application

def checkInHacker(application):
    checkin = CheckIn()
    checkin.application = application
    checkin.save()

def getNotCheckedInhackersList():
    hackersList = Application.objects.exclude(id__in=[checkin.application for checkin in CheckIn.objects.all()])
    return hackersList

class CheckInList(LoginRequiredMixin, TemplateView):
    template_name = 'templates/check-in-list.html'
    hackersList = getNotCheckedInhackersList()

class CheckInHacker(LoginRequiredMixin, TemplateView):
    template_name = 'check-in-hacker.hmtl'