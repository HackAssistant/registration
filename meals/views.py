from django.core.urlresolvers import reverse
from meals.models import Meal, Eaten, MEAL_TYPE
from meals.tables import MealsListTable, MealsListFilter, MealsUsersTable, MealsUsersFilter
from app.mixins import TabsViewMixin
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from app.views import TabsView
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from user.mixins import IsOrganizerMixin, IsVolunteerMixin


def organizer_tabs(user):
    if user.is_organizer:
        return [('Meals', reverse('meals_list'), False),
                ('Users', reverse('meals_users'), False)]
    return [('Meals', reverse('meals_list'), False), ]


class MealsList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
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


class MealsCheckin(IsVolunteerMixin, TabsView):
    template_name = 'meal_checkin.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def post(self, request, *args, **kwargs):
        return redirect('meals_list')
