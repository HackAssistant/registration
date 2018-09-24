from django.conf.urls import url
from meals import views


urlpatterns = [
    url(r'^list/$', views.MealsList.as_view(), name='meals_list'),
    url(r'^api/$', views.MealsApi.as_view(), name='meals_api')
]
