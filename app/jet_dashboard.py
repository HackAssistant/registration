from app import dashboard_modules
from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.available_children.append(modules.ModelList)
        self.available_children.append(modules.RecentActions)
        self.available_children.append(dashboard_modules.BestReviewers)
        self.available_children.append(dashboard_modules.AppsStats)
        self.children.append(modules.ModelList(
            _('Models'),
            column=1,
            order=0
        ))
        self.children.append(dashboard_modules.BestReviewers(
            _('Reviewer Leaderboard'),
            column=0, order=0)
        )
