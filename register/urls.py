from django.conf.urls import url
from register import views

urlpatterns = [
    url(r'applications/$', views.ApplicationListView.as_view()),
    url(r'applications/update$', views.UpdateApplications.as_view()),
    url(r'applications/(?P<token>\w+)/invite', views.InviteApplication.as_view(), name='invite_app'),
    url(r'applications/(?P<token>\w+)/confirm$', views.ConfirmApplication.as_view(), name='confirm_app')
]
