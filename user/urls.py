from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^login/$', views.login, name='account_login'),
    url(r'^callback/(?P<provider>[0-9A-Za-z_\-]+)/$', views.callback, name='callback'),
    url(r'^signup/$', views.signup, name='account_signup'),
    url(r'^logout/$', views.logout, name='account_logout'),
    url(r'^activate/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^password/$', views.set_password, name='set_password'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', views.password_reset_complete, name='password_reset_complete'),
    url(r'^verify/$', views.verify_email_required, name='verify_email_required'),
    url(r'^verify/send$', views.send_email_verification, name='send_email_verification'),
]
