from django.conf.urls import url

from judging import views

urlpatterns = [
    url(r'^import/$', views.ImportProjectsView.as_view(), name='import_projects'),
    # url(r'^projects/$', views.InviteListView.as_view(), name='project_list'),
]
