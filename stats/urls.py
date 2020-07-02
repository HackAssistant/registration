from django.conf import settings
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from stats import views

urlpatterns = [
    url(r'^api/apps/$', cache_page(5 * 60)(views.app_stats_api), name='api_app_stats'),
    url(r'^api/volunteer/$', cache_page(5 * 60)(views.volunteer_stats_api), name='api_volunteer_stats'),
    url(r'^api/reimb/$', cache_page(5 * 60)(views.reimb_stats_api), name='api_reimb_stats'),
    url(r'^api/users/$', cache_page(5 * 60)(views.users_stats_api), name='api_users_stats'),
    url(r'^api/checkin/$', cache_page(5 * 60)(views.checkin_stats_api), name='api_checkin_stats'),
    url(r'^apps/$', views.AppStats.as_view(), name='app_stats'),
    url(r'^volunteer/$', views.VolunteerStats.as_view(), name='volunteer_stats'),
    url(r'^users/$', views.UsersStats.as_view(), name='users_stats'),
    url(r'^checkin/$', views.CheckinStats.as_view(), name='checkin_stats'),

]


if getattr(settings, 'REIMBURSEMENT_ENABLED', False):
    urlpatterns.append(url(r'^reimb/$', views.ReimbStats.as_view(), name='reimb_stats'))
