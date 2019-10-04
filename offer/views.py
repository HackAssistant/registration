from app.utils import hacker_tabs
from app.views import TabsView
from offer.models import Code
from user.mixins import IsHackerMixin


class HackerOffers(IsHackerMixin, TabsView):
    template_name = 'offers.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerOffers, self).get_context_data(**kwargs)
        context["codes"] = Code.objects.filter(user_id=self.request.user.id).order_by("offer__order")
        return context
