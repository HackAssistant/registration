# Create your views here.
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from applications.models import APP_PENDING
from organizers import models
from organizers.tables import ApplicationsListTable, ApplicationFilter
from user.mixins import IsOrganizerMixin
from user.models import User


def add_vote(application, user, tech_rat, pers_rat):
    v = models.Vote()
    v.user = user
    v.application = application
    v.tech = tech_rat
    v.personal = pers_rat
    v.save()
    return v


def add_comment(application, user, text):
    comment = models.ApplicationComment()
    comment.author = user
    comment.application = application
    comment.text = text
    comment.save()
    return comment


class RankingView(IsOrganizerMixin, TemplateView):
    template_name = 'ranking.html'

    def get_context_data(self, **kwargs):
        context = super(RankingView, self).get_context_data(**kwargs)
        context['ranking'] = User.objects.annotate(
            vote_count=Count('vote__calculated_vote')) \
            .order_by('-vote_count').exclude(vote_count=0).values('vote_count',
                                                                  'email')
        return context


class ApplicationsListView(IsOrganizerMixin, SingleTableMixin, FilterView):
    template_name = 'applications_list.html'
    table_class = ApplicationsListTable
    filterset_class = ApplicationFilter
    table_pagination = {'per_page': 100}

    def get_queryset(self):
        return models.Application.annotate_vote(models.Application.objects.all())


class ApplicationDetailView(IsOrganizerMixin, TemplateView):
    template_name = 'application_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetailView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context['app'] = application
        context['vote'] = self.can_vote()
        context['comments'] = models.ApplicationComment.objects.filter(application=application)
        return context

    def can_vote(self):
        return False

    def get_application(self, kwargs):
        application_id = kwargs.get('id', None)
        if not application_id:
            raise Http404
        application = models.Application.objects.filter(uuid=application_id).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('app_id')
        comment_text = request.POST.get('comment_text', None)
        application = models.Application.objects.get(id=id_)

        add_comment(application, request.user, comment_text)
        return HttpResponseRedirect(reverse('app_detail', kwargs={'id': id_}))


class VoteApplicationView(ApplicationDetailView):
    def get_application(self, kwargs):
        """
        Django model to the rescue. This is transformed to an SQL sentence
        that does exactly what we need
        :return: pending aplication that has not been voted by the current
        user and that has less votes and its older
        """
        return models.Application.objects \
            .exclude(vote__user_id=self.request.user.id) \
            .filter(status=APP_PENDING) \
            .annotate(count=Count('vote__calculated_vote')) \
            .order_by('count', 'submission_date') \
            .first()

    def get(self, request, *args, **kwargs):
        r = super(VoteApplicationView, self).get(request, *args, **kwargs)
        if not self.get_application(kwargs):
            return HttpResponseRedirect(reverse('receipt_review'))
        return r

    def post(self, request, *args, **kwargs):
        tech_vote = request.POST.get('tech_rat', None)
        pers_vote = request.POST.get('pers_rat', None)
        comment_text = request.POST.get('comment_text', None)
        application = models.Application.objects.get(pk=request.POST.get('app_id'))
        try:
            if request.POST.get('skip'):
                add_vote(application, request.user, None, None)
            elif request.POST.get('add_comment'):
                add_comment(application, request.user, comment_text)
            else:
                add_vote(application, request.user, tech_vote, pers_vote)
        # If application has already been voted -> Skip and bring next
        # application
        except IntegrityError:
            pass
        return HttpResponseRedirect(reverse('vote'))

    def can_vote(self):
        return True
