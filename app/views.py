from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse


@login_required
def root_view(request):
    if request.user.has_perm('register.vote'):
        return HttpResponseRedirect(reverse('vote'))
    elif request.user.has_perm('register.checkin'):
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('register.profile'))
