from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from app import utils, mixins


def root_view(request):
    if not request.user.is_authenticated() and not utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_signup', kwargs={'type': 'hacker'}))
    elif not request.user.is_authenticated() and utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_login'))
    elif not request.user.has_usable_password():
        return HttpResponseRedirect(reverse('set_password'))
    elif not request.user.email_verified:
        return HttpResponseRedirect(reverse('verify_email_required'))
    elif request.user.is_organizer:
        return HttpResponseRedirect(reverse('review'))
    elif request.user.is_volunteer:
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('dashboard'))


def code_conduct(request):
    code_link = getattr(settings, 'CODE_CONDUCT_LINK', None)
    if code_link:
        return HttpResponseRedirect(code_link)
    return render(request, 'code_conduct.html')


class TabsView(mixins.TabsViewMixin, TemplateView):
    pass
