from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from app.emails import render_mail


@login_required
def root_view(request):
    if request.user.has_perm('register.vote'):
        return HttpResponseRedirect(reverse('vote'))
    elif request.user.has_perm('register.checkin'):
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('profile'))


@login_required
def view_email(request):
    msg = render_mail('test_email/test', ['test@hackupc.com'],
                      {'subject': 'TEST', 'fb': 'hackupc'})
    return HttpResponse(msg.body)
