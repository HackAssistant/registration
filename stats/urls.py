from django.conf.urls import url
from django.views.decorators.cache import cache_page

from stats import views

urlpatterns = [
    url(r'^api/apps/$', cache_page(60)(views.app_stats_api), name='api_app_stats'),
    url(r'^$', views.AppStats.as_view(), name='app_stats'),
]
