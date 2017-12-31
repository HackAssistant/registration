from django.conf.urls import url

from reimbursement import views

urlpatterns = [
    url(r'^dashboard/$', views.ReimbursementHacker.as_view(), name='reimbursement_dashboard'),
    url(r'^review/$', views.ReceiptReview.as_view(), name='receipt_review'),
    url(r'^send/$', views.SendReimbursementListView.as_view(), name='send_reimbursement'),
    url(r'^all/$', views.ReimbursementListView.as_view(), name='reimbursement_list'),
    url(r'^(?P<id>[\w-]+)$', views.ReimbursementDetail.as_view(), name='reimbursement_detail'),
]
