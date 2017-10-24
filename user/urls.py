from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'login/$', views.login, name='account_login'),
    url(r'signup/$', views.signup, name='account_signup'),
    url(r'logout/$', views.logout, name='account_logout'),

]
