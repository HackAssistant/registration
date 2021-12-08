from django.conf.urls import url
from hardware import views


urlpatterns = [
    url(r'^list/$', views.HardwareListView.as_view(), name='hw_list'),
    url(r'^admin/$', views.HardwareAdminView.as_view(), name='hw_admin'),
    url(r'^borrowings/$', views.HardwareBorrowingsView.as_view(), name='hw_borrowings'),
    url(r'^requests/$', views.HardwareAdminRequestsView.as_view(), name='hw_requests')
]
