from django.shortcuts import render
from django.views import generic
# Create your views here.
from register import models


class ApplicationListView(generic.ListView):
    model = models.Application.objects.all()
    context_object_name = 'applications'
    template_name = 'app_list.html'

