from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.utils import reverse
from reimbursement import forms, models
from reimbursement.tables import ReimbursementTable, ReimbursementFilter
from user.mixins import IsOrganizerMixin


class ReimbursementReceipt(LoginRequiredMixin, TemplateView):
    template_name = 'reimbursement.html'

    def get_context_data(self, **kwargs):
        c = super(ReimbursementReceipt, self).get_context_data(**kwargs)
        c.update({'form': forms.ReceiptSubmissionReceipt(instance=self.request.user.reimbursement)})
        return c

    def post(self, request, *args, **kwargs):
        try:
            form = forms.ReceiptSubmissionReceipt(request.POST, request.FILES, instance=request.user.reimbursement)
        except:
            form = forms.ReceiptSubmissionReceipt(request.POST, request.FILES)
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


class ReimbursementDetail(IsOrganizerMixin, TemplateView):
    template_name = 'reimbursement_review.html'

    def get_context_data(self, **kwargs):
        id_ = kwargs.get('id', None)
        reimb = get_object_or_404(models.Reimbursement, pk=id_)
        return {'reimb': reimb}


class ReceiptReview(ReimbursementDetail):
    def get_context_data(self, **kwargs):
        reimb = models.Reimbursement.objects.filter(status=models.RE_PEND_APPROVAL).order_by('-update_time').first()
        return {'reimb': reimb, 'reject_form': forms.RejectReceiptForm(instance=reimb), 'review': True,
                'accept_form': forms.AcceptReceiptForm(instance=reimb)}

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get('id', None)
        reimb = models.Reimbursement.objects.get(pk=id_)
        a_form = forms.AcceptReceiptForm(instance=reimb)
        r_form = forms.RejectReceiptForm(instance=reimb)

        if request.POST.get('accept', None):
            a_form = forms.AcceptReceiptForm(request.POST, instance=reimb)
            if a_form.is_valid():
                a_form.save(commit=False)
                a_form.instance.accept_receipt(request.user)
                a_form.save()
                messages.success(request, 'Receipt accepted')
            else:
                c = self.get_context_data()
                c.update({'reject_form': r_form,
                          'accept_form': a_form})
                return render(request, self.template_name, c)

        elif request.POST.get('reject', None):
            r_form = forms.RejectReceiptForm(request.POST, instance=reimb)
            if r_form.is_valid():
                r_form.save(commit=False)
                m = r_form.instance.reject_receipt(request.user, request)
                m.send()
                r_form.save()
                messages.success(request, 'Receipt rejected')
            else:
                c = self.get_context_data()
                c.update({'reject_form': r_form,
                          'accept_form': a_form})
                return render(request, self.template_name, c)

        return HttpResponseRedirect(reverse('receipt_review'))


class ReimbursementListView(IsOrganizerMixin, SingleTableMixin, FilterView):
    template_name = 'reimbursements_table.html'
    table_class = ReimbursementTable
    filterset_class = ReimbursementFilter

    def get_queryset(self):
        return models.Reimbursement.objects.all()
