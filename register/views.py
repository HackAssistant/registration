# Create your views here.
from __future__ import print_function
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView
from register import models
from register.forms import ApplicationsTypeform


class UpdateApplications(View):
    def get(self, request):
        return HttpResponse(ApplicationsTypeform().update_forms())

class VoteApplicationView(LoginRequiredMixin, TemplateView):

    login_url = '/accounts/login/'
    redirect_field_name = '/vote/'

    template_name = 'app_vote.html'


    def get_user_unvotted_applications(self):
        votes = list(models.Vote.objects.all())
        applications = list(models.Application.objects.all())
        for vote in votes:
            if (vote.user_id == self.request.user.id):
                applications.remove(vote.application)
        print(len(applications))
        return applications#sorted(applications, key=votes)

    def post(self, request, *args, **kwargs):
        if request.POST.get('Accept'):
            v = models.Vote()
            v.user_id = request.user.id
            applications = models.Application.objects.all()
            a = applications.first()
            v.application = a
            v.vote = 1
            v.save()

        if request.POST.get('Declone'):
            v = models.Vote()
            v.user_id = request.user.id
            applications = models.Application.objects.all()
            a = applications.first()
            v.application = a
            v.vote = -1
            v.save()

        if request.POST.get('Pass'):
            v = models.Vote()
            v.user_id = request.user.id
            applications = models.Application.objects.all()
            a = applications.first()
            v.application = a
            v.vote = 0
            v.save()

        return HttpResponseRedirect('/vote')

    def get_context_data(self, **kwargs):
        print ("asdasdasd")
        context = super(VoteApplicationView, self).get_context_data(**kwargs)
        applications = self.get_user_unvotted_applications()

        if len(applications) == 0:
            print("No applications")
            self.template_name = 'no_applications_left.html'
            context["title"] = "There are no applications to vote."
            return context

        a = applications[0]
        context["name"] = a.name
        context["from"] = a.country
        context["university"] = a.university
        context["degree"] = a.degree

        context["dp_image_src"] = "https://maxcdn.icons8.com/Share/icon/ios7/Logos//devpost1600.png"
        context["github_image_src"] = "https://cdn4.iconfinder.com/data/icons/iconsimple-logotypes/512/github-512.png"
        return context

class ConfirmApplication(TemplateView):
    template_name = 'confirm.html'

    def get_context_data(self, **kwargs):
        context = super(ConfirmApplication, self).get_context_data(**kwargs)
        application = models.Application.objects.get(id=context['token'])
        request = self.request
        try:
            application.confirm()
            context.update({
                'application': application,
                'cancel': application.cancelation_url(request)
            })
        except ValidationError:
            context.update({
                'error': "application can't be confirmed",
            })


        return context


class CancelApplication(View):
    def get(self, request, token):
        application = models.Application.objects.get(id=token)
        application.cancel()
        return HttpResponse('CANCELLED')
