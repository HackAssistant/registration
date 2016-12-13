from django.conf.urls import url, include


from register import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'applications/$', views.ApplicationListView.as_view()),
    url(r'applications/update$', views.UpdateApplications.as_view()),
]