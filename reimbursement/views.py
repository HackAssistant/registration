from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from app.utils import reverse
from reimbursement import forms


class ReimbursementReceipt(LoginRequiredMixin, TemplateView):
    template_name = 'reimbursement.html'

    def get_context_data(self, **kwargs):
        c = super(ReimbursementReceipt, self).get_context_data(**kwargs)
        c.update({'form': forms.ReimbursementForm(instance=self.request.user.reimbursement)})
        return c

    def post(self, request, *args, **kwargs):
        try:
            form = forms.ReimbursementForm(request.POST, request.FILES, instance=request.user.reimbursement)
        except:
            form = forms.ReimbursementForm(request.POST, request.FILES)
        if form.is_valid():
            reimb = form.save(commit=False)
            reimb.hacker = request.user
            reimb.save()
            messages.success(request,
                             'We have now received your reimbursement. '
                             'Processing will take some time, so please be patient.')

            return HttpResponseRedirect(reverse('root'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)
