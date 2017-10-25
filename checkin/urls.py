from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'^$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'^qr$', views.QRView.as_view(), name='check_in_qr'),
    url(r'^all/$', views.CheckInAllList.as_view(), name='check_in_all_list'),
    url(r'(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(),
        name='check_in_hacker'),
]
