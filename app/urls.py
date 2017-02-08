"""testP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic import RedirectView
from jet.dashboard.dashboard_modules import google_analytics_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # Auth views. Look at this in order to see who to use
    # https://docs.djangoproject.com/en/1.10/topics/auth/default/

    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/password/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^', include('register.urls')),
    url(r'^favicon.ico', RedirectView.as_view(url=static('favicon.ico'))),
    url(r'^', include('checkin.urls'))
]
