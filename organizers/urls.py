from django.conf.urls import url

from organizers import views

urlpatterns = [
    url(r'^review/$', views.ReviewApplicationView.as_view(), name='review'),
    url(r'^ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'^(?P<id>[\w-]+)$', views.ApplicationDetailView.as_view(), name="app_detail"),
    url(r'^all/$', views.ApplicationsListView.as_view(), name="app_list"),
    url(r'^all/invite/$', views.InviteListView.as_view(), name="invite_list"),
    url(r'^all/invite/teams/$', views.InviteTeamListView.as_view(), name="invite_teams_list"),
    url(r'^dubious/$', views.DubiousApplicationsListView.as_view(), name="dubious"),
    url(r'^volunteer/all/$', views.VolunteerApplicationsListView.as_view(), name="volunteer_list"),
    url(r'^volunteer/(?P<id>[\w-]+)$', views.ReviewVolunteerApplicationView.as_view(), name="volunteer_detail"),
    url(r'^sponsor/all/$', views.SponsorApplicationsListView.as_view(), name="sponsor_list"),
    url(r'^sponsor/(?P<id>[\w-]+)$', views.ReviewSponsorApplicationView.as_view(), name="sponsor_detail"),
    url(r'^mentor/all/$', views.MentorApplicationsListView.as_view(), name="mentor_list"),
    url(r'^mentor/(?P<id>[\w-]+)$', views.ReviewMentorApplicationView.as_view(), name="mentor_detail"),
    url(r'^user/sponsor/all/$', views.SponsorUserListView.as_view(), name="sponsor_user_list"),
]
