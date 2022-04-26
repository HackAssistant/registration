from django.conf.urls import url
from meals import views


urlpatterns = [
    url(r'^list/$', views.MealsList.as_view(), name='meals_list'),
    url(r'^activity/list/$', views.ActivitiesList.as_view(), name='activity_list'),
    url(r'^add/$', views.MealAdd.as_view(), name='meal_add'),
    url(r'^users/$', views.MealsUsers.as_view(), name='meals_users'),
    url(r'^activity/users/$', views.ActivitiesUsers.as_view(), name='activity_users'),
    url(r'^(?P<id>[\w-]+)$', views.MealDetail.as_view(), name='meal_detail'),
    url(r'^scan/(?P<id>[\w-]+)$', views.MealsCheckin.as_view(), name='meal_checkin'),
    url(r'^api/checkin$', views.MealsCoolAPI.as_view(), name='cool_meals_api')
]
