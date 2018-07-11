from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

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

class TabsView(mixins.TabsViewMixin, TemplateView):
    pass
