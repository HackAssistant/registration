from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^checkin/$', views.CheckInListView.as_view(), name='check_in_list'),
    url(r'checkin/hacker/(?P<id>[0-9]+)/$', views.CheckInHackerView.as_view(), name='check_in_hacker')
]