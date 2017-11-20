from django.conf.urls import url

from reimbursement import views

urlpatterns = [
    url(r'^submit/$', views.ReimbursementReceipt.as_view(), name='reimbursement_form'),
    url(r'^review/$', views.ReceiptReview.as_view(), name='receipt_review'),
    url(r'^send/$', views.SendReimbursementListView.as_view(), name='send_reimbursement'),
    url(r'^$', views.ReimbursementListView.as_view(), name='reimbursement_list'),
    url(r'^(?P<id>[\w-]+)$', views.ReimbursementDetail.as_view(), name='reimbursement_detail'),
]
