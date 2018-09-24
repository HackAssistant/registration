from django.core.urlresolvers import reverse
from meals.models import Meal, Eaten
from meals.tables import MealsListTable, MealsListFilter
from app.mixins import TabsViewMixin
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.core import serializers
from django.http import HttpResponse
from user.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
import datetime
from applications.models import Application

token = 'felix'


def organizer_tabs(user):
    t = [('List', reverse('meals_list'), False), ]
    return t


class MealsList(TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_list.html'
    table_class = MealsListTable
    filterset_class = MealsListFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Meal.objects.filter()


class MealsApi(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != token:
            return HttpResponse('{"code": 1, "message": "Invalid token"}', content_type='application/json')
        var_object = request.GET.get('object')
        if var_object not in ['meal']:
            return HttpResponse('{"code": 1, "message": "Invalid object"}', content_type='application/json')

        meals = Meal.objects.filter(ends__gt=datetime.datetime.now()).order_by('starts')
        var_all = request.GET.get('all')
        if var_all == '1':
            meals = Meal.objects.all().order_by('starts')
        meals_data = serializers.serialize('json', meals)
        return HttpResponse('{"code": 0, "content": ' + meals_data + '}', content_type='application/json')

    def post(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != token:
            return HttpResponse('{"code": 1, "message": "Invalid token"}', content_type='application/json')
        var_object = request.GET.get('object')
        if var_object not in ['user', 'meal']:
            return HttpResponse('{"code": 1, "message": "Invalid object"}', content_type='application/json')

        var_meal = request.GET.get('meal')
        obj_meal = Meal.objects.filter(id=var_meal).first()
        if obj_meal is None:
            return HttpResponse('{"code": 1, "message": "Invalid meal"}', content_type='application/json')
        if var_object == 'user':
            var_repetitions = obj_meal.times
            var_user = request.GET.get('user')
            obj_user = User.objects.filter(id=var_user).first()
            if obj_user is None:
                return HttpResponse('{"code": 1, "message": "Invalid user"}', content_type='application/json')
            var_name = obj_user.name
            obj_application = Application.objects.filter(user=obj_user).first()
            if obj_application is None:
                return HttpResponse('{"code": 1, "message": "No application found"}', content_type='application/json')
            var_diet = obj_application.diet
            var_eatens = Eaten.objects.filter(meal=obj_meal, user=obj_user).count()
            if var_eatens >= var_repetitions:
                return HttpResponse('{"code": 2, "message": "Hacker alreay ate"}', content_type='application/json')
            obj_eaten = Eaten()
            obj_eaten.meal = obj_meal
            obj_eaten.user = obj_user
            obj_eaten.save()
            return HttpResponse('{"code": 0, "content": {"name": ' + var_name + ', "diet": ' + var_diet + '}}',
                                content_type='application/json')
        var_repetitions = request.GET.get('times')
        obj_meal.times = var_repetitions
        obj_meal.save()
        return HttpResponse('{"code": 0, "message": "Times updated"}', content_type='application/json')
