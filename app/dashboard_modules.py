from django import forms
from django.contrib.auth.models import User
from django.db.models import Count
from jet.dashboard.modules import DashboardModule


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
