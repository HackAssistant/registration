from django.conf.urls import url

from register import views

urlpatterns = [
    url(r'application/confirm$', views.ConfirmApplication.as_view(),
        name='confirm_app'),
    url(r'application/cancel$', views.CancelApplication.as_view(),
        name='cancel_app'),
    url(r'vote/$', views.VoteApplicationView.as_view(), name='vote'),
    url(r'ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'dashboard/$', views.HackerDashboard.as_view(), name='dashboard'),
    url(r'profile/$', views.ProfileHacker.as_view(), name='profile'),
    url(r'applications/new$', views.ApplyHacker.as_view(), name='apply'),
    url(r'applications/fetch$', views.fetch_application, name='fetch_application'),
    url(r'applications/fetch/all$', views.retrieve_all_applications, name='retrieve_all_applications'),
    url(r'applications/(?P<id>\w+)$', views.ApplicationDetailView.as_view(), name="app_detail"),
    url(r'applications/$', views.ApplicationsListView.as_view(), name="app_list")
]
