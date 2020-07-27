from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^hacker/all/$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'(?P<type>[a-z_\-]{1,10})/(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(),
        name='check_in_hacker'),
    url(r'^volunteer/all/$', views.CheckinVolunteerList.as_view(), name='check_in_volunteer_list'),
    url(r'^mentor/all/$', views.CheckinMentorList.as_view(), name='check_in_mentor_list'),
    url(r'^sponsor/all/$', views.CheckinSponsorList.as_view(), name='check_in_sponsor_list'),
]
