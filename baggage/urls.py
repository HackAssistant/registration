from django.conf.urls import url
from baggage import views


urlpatterns = [
    url(r'^search/$', views.BaggageUsers.as_view(), name='baggage_search'),
    url(r'^out/$', views.BaggageList.as_view(), name='baggage_list'),
    url(r'^in/(?P<new_id>[\w-]+)$', views.BaggageAdd.as_view(), name='baggage_new'),
    url(r'^(?P<first>[\w-]+\/)?(?P<id>[\w-]+)$', views.BaggageDetail.as_view(), name='baggage_detail')
]