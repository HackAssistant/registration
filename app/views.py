from django.http import HttpResponseRedirect
from django.urls import reverse


def root_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_signup'))
    if request.user.is_organizer:
        return HttpResponseRedirect(reverse('vote'))
    elif request.user.is_volunteer:
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('dashboard'))
