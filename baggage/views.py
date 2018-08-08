from django.shortcuts import render
from app.mixins import TabsViewMixin
from user.mixins import IsOrganizerMixin, IsDirectorMixin
from django_tables2 import SingleTableMixin
from django.views.generic import TemplateView

class BaggageList(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.all())