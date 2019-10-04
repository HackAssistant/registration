from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from applications.models import Application
from offer.models import Offer
from reimbursement.models import Reimbursement
from baggage.models import Bag
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
import os

from app import utils, mixins


def root_view(request):
    if not request.user.is_authenticated() and not utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_signup'))
    if not request.user.is_authenticated() and utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_login'))
    if not request.user.has_usable_password():
        return HttpResponseRedirect(reverse('set_password'))
    if not request.user.email_verified:
        return HttpResponseRedirect(reverse('verify_email_required'))
    if request.user.is_organizer:
        return HttpResponseRedirect(reverse('review'))
    elif request.user.is_volunteer:
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('dashboard'))


def code_conduct(request):
    code_link = getattr(settings, 'CODE_CONDUCT_LINK', None)
    if code_link:
        return HttpResponseRedirect(code_link)
    return render(request, 'code_conduct.html')


def legal_notice(request):
    return render(request, 'legal_notice.html')


def privacy_and_cookies(request):
    return render(request, 'privacy_and_cookies.html')


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')


def protectedMedia(request, file_):
    path, file_name = os.path.split(file_)
    downloadable_path = None
    if path == "resumes":
        app = get_object_or_404(Application, resume=file_)
        if request.user.is_authenticated() and (request.user.is_organizer or
                                                (app and (app.user_id == request.user.id))):
            downloadable_path = app.resume.path
    elif path == "receipt":
        app = get_object_or_404(Reimbursement, receipt=file_)
        if request.user.is_authenticated() and (request.user.is_organizer or
                                                (app and (app.hacker_id == request.user.id))):
            downloadable_path = app.receipt.path
    elif path == "baggage":
        bag = get_object_or_404(Bag, image=file_)
        if request.user.is_authenticated() and (request.user.is_organizer or request.user.is_volunteer):
            downloadable_path = bag.image.path
    elif path == "offer/logo":
        offer = get_object_or_404(Offer, logo=file_)
        downloadable_path = offer.logo.path
    if downloadable_path:
        response = StreamingHttpResponse(open(downloadable_path, 'rb'))
        response['Content-Type'] = ''
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % file_name
        response['Content-Transfer-Encoding'] = 'binary'
        response['Expires'] = '0'
        response['Cache-Control'] = 'must-revalidate'
        response['Pragma'] = 'public'
        return response
    return HttpResponseRedirect(reverse('account_login'))


class TabsView(mixins.TabsViewMixin, TemplateView):
    pass
