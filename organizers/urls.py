from django.conf.urls import url

from organizers import views

urlpatterns = [
    url(r'^vote/$', views.VoteApplicationView.as_view(), name='vote'),
    url(r'^ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'^applications/(?P<id>[\w-]+)$', views.ApplicationDetailView.as_view(), name="app_detail"),
    url(r'^applications/$', views.ApplicationsListView.as_view(), name="app_list")
]
