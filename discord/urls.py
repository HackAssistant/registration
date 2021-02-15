from django.conf.urls import url
from discord import views

urlpatterns = [
    url(r'^connect/$', views.ConnectDiscord.as_view(), name='discord_login'),
    url(r'^oauth2/$', views.RedirectDiscord.as_view(), name='discord_redirect'),
]
