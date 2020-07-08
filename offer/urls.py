from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from offer import views

urlpatterns = [
    url(r'^codes/$', login_required(views.HackerOffers.as_view()), name='codes'),
]
