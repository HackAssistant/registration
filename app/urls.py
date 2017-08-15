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
from app import views
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # Auth views. Look at this in order to see who to use
    # https://docs.djangoproject.com/en/1.10/topics/auth/default/

    url(r'^accounts/', include('allauth.urls')),
    url(r'^table/', include('table.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include(
        'jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^', include('register.urls')),
    url(r'^$', views.root_view, name='root'),
    url(r'^email-test$', views.view_email, name='email-test'),
    url(r'^favicon.ico', RedirectView.as_view(url=static('favicon.ico'))),
    url(r'^checkin/', include('checkin.urls')),
]
