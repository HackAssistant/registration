from django import forms
from django.contrib.auth.models import User
from django.db.models import Count
from jet.dashboard.modules import DashboardModule


class LinkListSettingsForm(forms.Form):
    layout = forms.IntegerField(label='Limit', min_value=1)


class BestReviewers(DashboardModule):
    title = 'Recent tickets'
    template = 'modules/reviewers.html'
    limit = 10

    def settings_dict(self):
        return {
            'limit': self.limit
        }

    def load_settings(self, settings):
        self.limit = settings.get('limit', self.layout)

    def init_with_context(self, context):
        self.children = User.objects.annotate(vote_count=Count('vote__calculated_vote')) \
                            .order_by('-vote_count')[:self.limit]
