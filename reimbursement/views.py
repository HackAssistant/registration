from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from reimbursement import forms


class ReimbursementReceipt(LoginRequiredMixin, TemplateView):
    template_name = 'reimbursement.html'

    def get_context_data(self, **kwargs):
        c = super(ReimbursementReceipt, self).get_context_data(**kwargs)
        c.update({'form': forms.ReimbursementForm(instance=self.request.user.reimbursement)})
        return c
