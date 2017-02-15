from django import forms
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from jet.dashboard.modules import DashboardModule
from register.models import Application, STATUS


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
        self.children = User.objects.annotate(vote_count=Count('vote__calculated_vote')) \
                            .order_by('-vote_count')[:self.limit]


class AppsStatsForm(forms.Form):
    status = forms.ChoiceField(label='Status', choices=STATUS+[('__all__','All')])


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

        if self.status != '__all__':
            qs = qs.filter(status=self.status)

        self.tshirts = qs.values('tshirt_size').annotate(count=Count('tshirt_size'))
        self.diets = qs.values('diet').annotate(count=Count('diet'))
        self.amount = qs.aggregate(total=Sum('reimbursement_money'))
        self.count_status = Application.objects.all().values('status').annotate(count=Count('status'))
