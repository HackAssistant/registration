from app import dashboard_modules
from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.available_children.append(modules.ModelList)
        self.children.append(modules.LinkList(
            _('HackUPC URLs'),
            children=[
                {
                    'title': _('HackUPC Landing'),
                    'url': 'https://hackupc.com/',
                    'external': True,
                },
                {
                    'title': _('Sendgrid'),
                    'url': 'https://sendgrid.com',
                    'external': True,
                },
                {
                    'title': _('HackUPC Live'),
                    'url': 'https://hackupc.com/live',
                    'external': True,
                },
            ],
            column=2,
            order=0
        ))
        self.children.append(modules.ModelList(
            _('Models'),
            column=0,
            order=0
        ))
        self.children.append(dashboard_modules.BestReviewers(_('Reviewer Leaderboard'), column=1, order=0))
