from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'add/session/(?P<type>[\w]+)$', views.CheckInSession.as_view(),
        name='check_in_session'),
    url(r'^type/$', views.CheckInType.as_view(), name='check_in_type'),
    url(r'^all/$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'^qr$', views.QRView.as_view(), name='check_in_qr'),
    url(r'(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(),
        name='check_in_hacker'),
]
