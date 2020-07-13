from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^all/$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'^ranking/$', views.CheckinRankingView.as_view(), name='check_in_ranking'),
    url(r'(?P<type>[a-z_\-]{1,10})/(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(),
        name='check_in_hacker'),
    url(r'^volunteer/$', views.CheckinVolunteerList.as_view(), name='check_in_volunteer_list'),
    url(r'^mentor/$', views.CheckinMentorList.as_view(), name='check_in_mentor_list'),
    url(r'^sponsor/$', views.CheckinSponsorList.as_view(), name='check_in_sponsor_list'),
]
