from django.conf.urls import url
from baggage import views


urlpatterns = [
    url(r'^all/$', views.BaggageList.as_view(), name="baggage_list"),
    url(r'^in/$', views.BaggageAdd.as_view(), name="baggage_add"),
    url(r'^out/$', views.BaggageDel.as_view(), name="baggage_del")
]