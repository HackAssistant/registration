from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^all/$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'^all/sponsor/$', views.CheckInSponsorList.as_view(), name='check_in_list_sponsor'),
    url(r'^all/mentor/$', views.CheckInMentorList.as_view(), name='check_in_list_mentor'),
    url(r'^all/judge/$', views.CheckInJudgeList.as_view(), name='check_in_list_judge'),
    url(r'^all/volunteer/$', views.CheckInVolunteerList.as_view(), name='check_in_list_volunteer'),
    url(r'^ranking/$', views.CheckinRankingView.as_view(), name='check_in_ranking'),
    url(r'(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(),
        name='check_in_hacker'),
    url(r'^api/$', views.CheckInAPI.as_view(), name='check_in_api'),
]
