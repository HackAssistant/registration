from django.core.urlresolvers import reverse
from meals.models import Meal, Eaten, MEAL_TYPE
from meals.tables import MealsListTable, MealsListFilter, MealsUsersTable, MealsUsersFilter
from app.mixins import TabsViewMixin
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.core import serializers
from django.http import HttpResponse
from user.models import User
from checkin.models import CheckIn
from applications.models import Application
from app.views import TabsView
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
import json
from django.conf import settings
from user.mixins import IsOrganizerMixin


def organizer_tabs(user):
    t = [('Meals', reverse('meals_list'), False),
         ('Users', reverse('meals_users'), False)]
    return t


class MealsList(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_list.html'
    table_class = MealsListTable
    filterset_class = MealsListFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Meal.objects.filter()


class MealsUsers(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_users.html'
    table_class = MealsUsersTable
    filterset_class = MealsUsersFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Eaten.objects.filter()


class MealDetail(IsOrganizerMixin, TabsView):
    template_name = 'meal_detail.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(MealDetail, self).get_context_data(**kwargs)
        mealid = kwargs['id']
        meal = Meal.objects.filter(id=mealid).first()
        if not meal:
            raise Http404
        context.update({
            'meal': meal,
            'types': MEAL_TYPE,
            'starts': meal.starts.strftime("%Y-%m-%d %H:%M:%S"),
            'ends': meal.ends.strftime("%Y-%m-%d %H:%M:%S"),
            'eaten': meal.eaten()
        })
        return context

    def post(self, request, *args, **kwargs):
        mealid = request.POST.get('meal_id')
        meal = Meal.objects.filter(id=mealid).first()
        mealname = request.POST.get('meal_name')
        if mealname:
            meal.name = mealname
        mealtype = request.POST.get('meal_type')
        if mealtype:
            meal.kind = mealtype
        mealstarts = request.POST.get('meal_starts')
        if mealstarts:
            meal.starts = mealstarts
        mealends = request.POST.get('meal_ends')
        if mealends:
            meal.ends = mealends
        mealtimes = request.POST.get('meal_times')
        if mealtimes:
            meal.times = mealtimes
        meal.save()
        messages.success(self.request, 'Meal updated!')
        return redirect('meals_list')


class MealAdd(IsOrganizerMixin, TabsView):
    template_name = 'meal_add.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(MealAdd, self).get_context_data(**kwargs)
        context.update({
            'types': MEAL_TYPE,
            'time1': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'time2': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return context

    def post(self, request, *args, **kwargs):
        meal = Meal()
        mealname = request.POST.get('meal_name')
        if mealname:
            meal.name = mealname
        mealtype = request.POST.get('meal_type')
        if mealtype:
            meal.kind = mealtype
        mealstarts = request.POST.get('meal_starts')
        if mealstarts:
            meal.starts = mealstarts
        mealends = request.POST.get('meal_ends')
        if mealends:
            meal.ends = mealends
        mealtimes = request.POST.get('meal_times')
        if mealtimes:
            meal.times = mealtimes
        meal.save()
        messages.success(self.request, 'Meal added!')
        return redirect('meals_list')


class MealsApi(TabsView):

    def get(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != settings.MEALS_TOKEN:
            return HttpResponse(status=500)
        var_object = request.GET.get('object')
        if var_object not in ['meal']:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid object'}), content_type='application/json')

        meals = Meal.objects.filter(ends__gt=datetime.now()).order_by('starts')
        var_all = request.GET.get('all')
        if var_all == '1':
            meals = Meal.objects.all().order_by('starts')
        meals_data = serializers.serialize('json', meals)
        return HttpResponse(json.dumps({'code': 0, 'content': json.loads(meals_data)}), content_type='application/json')

    def post(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != settings.MEALS_TOKEN:
            return HttpResponse(status=500)
        var_object = request.GET.get('object')
        if var_object not in ['user', 'meal']:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid object'}), content_type='application/json')

        var_meal = request.GET.get('meal')
        obj_meal = Meal.objects.filter(id=var_meal).first()
        if obj_meal is None:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid meal'}), content_type='application/json')
        if var_object == 'user':
            var_repetitions = obj_meal.times
            var_user = request.GET.get('user')
            obj_checkin = CheckIn.objects.filter(qr_identifier=var_user).first()
            if obj_checkin is None:
                return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid user'}), content_type='application/json')
            obj_application = obj_checkin.application
            obj_user = obj_application.user
            if obj_application is None:
                return HttpResponse(json.dumps({'code': 1, 'message': 'No application found'}),
                                    content_type='application/json')
            var_diet = obj_application.diet
            var_eatens = Eaten.objects.filter(meal=obj_meal, user=obj_user).count()
            if var_eatens >= var_repetitions:
                return HttpResponse(json.dumps({'code': 2, 'message': 'Hacker alreay ate'}),
                                    content_type='application/json')
            obj_eaten = Eaten()
            obj_eaten.meal = obj_meal
            obj_eaten.user = obj_user
            obj_eaten.save()
            return HttpResponse(json.dumps({'code': 0, 'content': {'diet': var_diet}}),
                                content_type='application/json')
        var_repetitions = request.GET.get('times')
        obj_meal.times = var_repetitions
        obj_meal.save()
        return HttpResponse(json.dumps({'code': 0, 'message': 'Times updated'}), content_type='application/json')
