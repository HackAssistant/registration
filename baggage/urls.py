from django.conf.urls import url
from baggage import views


urlpatterns = [
    url(r'^all/$', views.BaggageList.as_view(), name="baggage_list")
]