from django.conf.urls import url

from applications import views

urlpatterns = [
    url(r'applications/(?P<id>[\w-]+)/confirm$', views.ConfirmApplication.as_view(),
        name='confirm_app'),
    url(r'applications/(?P<id>[\w-]+)/cancel$', views.CancelApplication.as_view(),
        name='cancel_app'),
    url(r'dashboard/$', views.HackerDashboard.as_view(), name='dashboard'),
    url(r'code_conduct/$', views.code_conduct, name='code_conduct'),
]
