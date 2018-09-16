from django.conf.urls import url
from baggage import views


urlpatterns = [
    url(r'^in/$', views.BaggageAdd.as_view(), name="baggage_add"),
    url(r'^out/$', views.BaggageList.as_view(), name="baggage_list"),
    url(r'(?P<id>[\w-]+)$', views.BaggageDetail.as_view(), name='baggage_detail')
]