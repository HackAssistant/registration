from django.conf.urls import url

from organizers import views

urlpatterns = [
    url(r'^review/$', views.ReviewApplicationView.as_view(), name='review'),
    url(r'^ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'^(?P<id>[\w-]+)$', views.ApplicationDetailView.as_view(), name="app_detail"),
    url(r'^$', views.ApplicationsListView.as_view(), name="app_list"),
    url(r'^invite/$', views.InviteListView.as_view(), name="invite_list")
]
