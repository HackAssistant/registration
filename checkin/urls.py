from django.conf.urls import url
from checkin import views

urlpatterns = [
    url(r'checkin/', views.CheckInList.as_view()),
    url(r'checkin/(?P<hacker>\w+)/', views.CheckInHacker.as_view(), name='check_in_hacker')
]