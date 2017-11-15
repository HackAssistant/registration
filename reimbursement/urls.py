from django.conf.urls import url

from reimbursement import views

urlpatterns = [
    url(r'^submit/$', views.ReimbursementReceipt.as_view(), name='reimbursement_form'),
    url(r'^review/$', views.ReceiptReview.as_view(), name='receipt_review'),
]
