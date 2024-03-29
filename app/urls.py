from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user.urls')),
    # url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    # url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^applications/', include('organizers.urls')),
    url(r'^', include('applications.urls')),
    url(r'^$', views.root_view, name='root'),
    url(r'^favicon.ico', RedirectView.as_view(url=static('favicon.ico'))),
    url(r'^checkin/', include('checkin.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'code_conduct/$', views.code_conduct, name='code_conduct'),
    url(r'^files/(?P<file_>.*)$', views.protectedMedia, name="protect_media"),

]

if settings.REIMBURSEMENT_ENABLED:
    urlpatterns.append(url(r'^reimbursement/', include('reimbursement.urls')))

if settings.HARDWARE_ENABLED:
    urlpatterns.append(url(r'^hardware/', include('hardware.urls')))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
