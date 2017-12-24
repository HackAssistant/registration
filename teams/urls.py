from django.conf.urls import url

from teams import views

urlpatterns = [
    url(r'^$', views.HackerTeam.as_view(), name='teams'),
]
