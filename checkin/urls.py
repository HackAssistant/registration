from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^checkin/', views.CheckInListView.as_view(), name='check_in_list'),
    url(r'^hacker/(?P<id>\d+)/', views.CheckInHackerView.as_view(), name='check_in_hacker')
]