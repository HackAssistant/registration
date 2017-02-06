from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.db import models

from django.urls import reverse
from django.views.generic import TemplateView
from models import CheckIn

from tables import ApplicationsTable

from register.models import Application


def checkInHacker(application):
    checkin = CheckIn()
    checkin.application = application
    checkin.save()


def getNotCheckedInhackersList():
    hackersList = Application.objects.exclude(id__in=[checkin.application.id for checkin in CheckIn.objects.all()])
    return hackersList


class CheckInListView(LoginRequiredMixin, TemplateView):
    template_name = 'templates/check-in-list.html'
    hackersList = getNotCheckedInhackersList()

    def get_context_data(self, **kwargs):
        context = super(CheckInListView, self).get_context_data(**kwargs)
        applications = getNotCheckedInhackersList()
        context['applications'] = applications
        applicationsTable = ApplicationsTable(applications)
        context['applicationsTable'] = applicationsTable
        return context

class CheckInHackerView(LoginRequiredMixin, TemplateView):
    template_name = 'templates/check-in-hacker.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = int(kwargs['id'])
        app = Application.objects.filter(id=appid)[0]
        context.update({
            'app': app,
        })
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        app = Application.objects.filter(id=appid)[0]
        checkInHacker(app)
        url = reverse('check_in_list')
        return HttpResponseRedirect(url)