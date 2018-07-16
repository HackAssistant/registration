from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse
from applications.models import Application

from app import utils, mixins


def root_view(request):
    if not request.user.is_authenticated() and not utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_signup'))
    if not request.user.is_authenticated() and utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_login'))
    if not request.user.email_verified:
        return HttpResponseRedirect(reverse('verify_email_required'))
    if request.user.is_organizer:
        return HttpResponseRedirect(reverse('review'))
    elif request.user.is_volunteer:
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('dashboard'))


def code_conduct(request):
    return render(request, 'code_conduct.html')


def legal_notice(request):
    return render(request, 'legal_notice.html')


def privacy_and_cookies(request):
    return render(request, 'privacy_and_cookies.html')


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')
  
  

def protectedMedia(request):
    current_resume = request.path.split("/",1)[1].split("/",1)[1]
    resume_owner = Application.objects.filter(resume=current_resume).first()
    if request.user.is_authenticated() and (request.user.is_organizer or (current_resume and (resume_owner.user_id == request.user.id))):
        response = HttpResponse('')
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = request.path
        return response
    return HttpResponseRedirect(reverse('account_login'))


class TabsView(mixins.TabsViewMixin, TemplateView):
    pass
