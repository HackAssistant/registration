from django import forms
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from jet.dashboard.modules import DashboardModule
from register.models import Application, STATUS
from reimbursement.models import Reimbursement, RE_SENT


class BestReviewerForm(forms.Form):
    limit = forms.IntegerField(label='Reviewers shown', min_value=1)


class BestReviewers(DashboardModule):
    title = 'Best reviewers'
    template = 'modules/reviewers.html'
    limit = 10
    settings_form = BestReviewerForm

    def settings_dict(self):
        return {
            'limit': self.limit
        }

    def load_settings(self, settings):
        self.limit = settings.get('limit', self.limit)

    def init_with_context(self, context):
        self.children = User.objects.annotate(
            vote_count=Count('vote__calculated_vote')).exclude(vote_count=0).order_by('-vote_count')[:self.limit]


class AppsStatsForm(forms.Form):
    status = forms.ChoiceField(label='Status',
                               choices=STATUS + [('__all__', 'All')])


class AppsStats(DashboardModule):
    title = 'Stats'
    template = 'modules/stats.html'
    status = '__all__'
    settings_form = AppsStatsForm

    def settings_dict(self):
        return {
            'status': self.status
        }

    def load_settings(self, settings):
        self.status = settings.get('status', self.status)

    def init_with_context(self, context):
        qs = Application.objects.all()
        reimb = Reimbursement.objects.all()

        if self.status != '__all__':
            qs = qs.filter(status=self.status)

        self.tshirts = qs.values('hacker__tshirt_size') \
            .annotate(count=Count('hacker__tshirt_size'))
        self.diets = qs.values('hacker__diet').annotate(count=Count('hacker__diet'))
        self.amount__assigned = reimb.aggregate(total=Sum('assigned_money'))
        self.amount__sent = reimb.filter(status=RE_SENT).aggregate(total=Sum('assigned_money'))
        self.count_status = Application.objects.all().values('status') \
            .annotate(count=Count('status'))


class RetrieveAllApplications(DashboardModule):
    title = 'Retrieve all applications'
    template = 'modules/retrieve.html'
    limit = 10
    settings_form = BestReviewerForm

    def settings_dict(self):
        return {
            'limit': self.limit
        }

    def load_settings(self, settings):
        self.limit = settings.get('limit', self.limit)

    def init_with_context(self, context):
        self.children = User.objects.annotate(
            vote_count=Count('vote__calculated_vote')).exclude(vote_count=0).order_by('-vote_count')[:self.limit]
