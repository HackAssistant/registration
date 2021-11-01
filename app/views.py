import os
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponseRedirect, StreamingHttpResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from app import utils, mixins
from applications.models import HackerApplication, MentorApplication

from offer.models import Offer

if getattr(settings, 'REIMBURSEMENT_ENABLED', False):
    from reimbursement.models import Reimbursement

if getattr(settings, 'BAGGAGE_ENABLED', False):
    from baggage.models import Bag


def root_view(request):
    if not request.user.is_authenticated and not utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_signup'))
    if not request.user.is_authenticated and utils.is_app_closed():
        return HttpResponseRedirect(reverse('account_login'))
    if not request.user.has_usable_password():
        return HttpResponseRedirect(reverse('set_password'))
    if not request.user.email_verified:
        return HttpResponseRedirect(reverse('verify_email_required'))
    if request.user.is_sponsor():
        return HttpResponseRedirect(reverse('sponsor_dashboard'))
    if request.user.is_organizer:
        return HttpResponseRedirect(reverse('review'))
    if request.user.is_volunteer_accepted:
        return HttpResponseRedirect(reverse('check_in_list'))
    return HttpResponseRedirect(reverse('dashboard'))


def code_conduct(request):
    code_link = getattr(settings, 'CODE_CONDUCT_LINK', None)
    if code_link:
        return HttpResponseRedirect(code_link)
    return render(request, 'code_conduct.html')


def legal_notice(request):
    legal_link = getattr(settings, 'LEGAL_LINK', None)
    if legal_link:
        return HttpResponseRedirect(legal_link)
    return render(request, 'legal_notice.html')


def privacy_and_cookies(request):
    privacy_link = getattr(settings, 'PRIVACY_LINK', None)
    if privacy_link:
        return HttpResponseRedirect(privacy_link)
    return render(request, 'privacy_and_cookies.html')


def terms_and_conditions(request):
    terms_link = getattr(settings, 'TERMS_LINK', None)
    if terms_link:
        return HttpResponseRedirect(terms_link)
    return render(request, 'terms_and_conditions.html')


def protectedMedia(request, file_):
    path, file_name = os.path.split(file_)
    downloadable_path = None
    if path.startswith("resumes"):
        try:
            app = HackerApplication.objects.get(resume=file_)
        except HackerApplication.DoesNotExist:
            try:
                app = MentorApplication.objects.get(resume=file_)
            except MentorApplication.DoesNotExist:
                raise Http404
        if request.user.is_authenticated and (request.user.is_organizer or
                                              (app and (app.user_id == request.user.id))):
            downloadable_path = app.resume.path
    elif path == "receipt":
        if getattr(settings, 'REIMBURSEMENT_ENABLED'):
            app = get_object_or_404(Reimbursement, receipt=file_)
            if request.user.is_authenticated and (request.user.is_organizer or
                                                  (app and (app.hacker_id == request.user.id))):
                downloadable_path = app.receipt.path
    elif path == "baggage":
        bag = get_object_or_404(Bag, image=file_)
        if request.user.is_authenticated and (request.user.is_organizer or request.user.is_volunteer):
            downloadable_path = bag.image.path
    elif path == "offer/logo":
        offer = get_object_or_404(Offer, logo=file_)
        downloadable_path = offer.logo.path
    if downloadable_path:
        (_, doc_extension) = file_name.rsplit('.', 1)
        if doc_extension == 'pdf':
            with open(downloadable_path, 'rb') as doc:
                response = HttpResponse(doc.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline;filename=%s' % quote(file_name)
                return response
            doc.closed
        else:
            response = StreamingHttpResponse(open(downloadable_path, 'rb'))
            response['Content-Type'] = ''
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % quote(file_name)
            response['Content-Transfer-Encoding'] = 'binary'
            response['Expires'] = '0'
            response['Cache-Control'] = 'must-revalidate'
            response['Pragma'] = 'public'
            return response
    return HttpResponseRedirect(reverse('account_login'))


class TabsView(mixins.TabsViewMixin, TemplateView):
    pass
