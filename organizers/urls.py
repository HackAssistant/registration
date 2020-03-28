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
    url(r'^blacklist/$', views.BlacklistApplicationsListView.as_view(), name="blacklist"),
]
