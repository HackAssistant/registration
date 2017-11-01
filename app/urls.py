from app import views
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user.urls')),
    url(r'^table/', include('table.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include(
        'jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^', include('organizers.urls')),
    url(r'^', include('hackers.urls')),
    url(r'^$', views.root_view, name='root'),
    url(r'^favicon.ico', RedirectView.as_view(url=static('favicon.ico'))),
    url(r'^checkin/', include('checkin.urls')),
]
