# Create your views here.
from django.http import HttpResponse
from django.views import View
from register import models, serializers
from register.forms import TypeformFetcher
from rest_framework import generics


class ApplicationListView(generics.ListAPIView):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationsSerializer


class UpdateApplications(View):
    def get(self, request):
        return HttpResponse(TypeformFetcher().update_forms())
