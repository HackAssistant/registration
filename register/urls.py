from django.conf.urls import url

from register import views

urlpatterns = [
    url(r'applications/(?P<token>\w+)/confirm$', views.ConfirmApplication.as_view(), name='confirm_app'),
    url(r'applications/(?P<token>\w+)/cancel$', views.CancelApplication.as_view(), name='cancel_app'),
    url(r'vote/$', views.VoteApplicationView.as_view(), name='vote'),
    url(r'ranking/$', views.RankingView.as_view(), name='ranking'),
    url(r'profile/', views.ProfileHacker.as_view(), name='profile')
]
