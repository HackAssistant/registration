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

# TODO: Set actions to POST
class ConfirmApplication(View):
    def get(self, request, token):
        application = models.Application.objects.get(id=token)
        application.confirm()
        return HttpResponse('CONFIRMED')


class InviteApplication(View):
    def get(self, request, token):
        application = models.Application.objects.get(id=token)
        application.invite(request)
        return HttpResponse('INVITED')


class CancelApplication(View):
    def get(self, request, token):
        application = models.Application.objects.get(id=token)
        application.cancel()
        return HttpResponse('CANCELLED')