from django.conf.urls import url
from django.views.decorators.cache import cache_page

from stats import views

urlpatterns = [
    url(r'^api/apps/$', cache_page(60)(views.app_stats_api), name='api_app_stats'),
    url(r'^api/reimb/$', cache_page(60)(views.reimb_stats_api), name='api_reimb_stats'),
    url(r'^apps/$', views.AppStats.as_view(), name='app_stats'),
    url(r'^reimb/$', views.ReimbStats.as_view(), name='reimb_stats'),
]
