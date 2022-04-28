from datetime import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from app.views import TabsView
from applications import models as models_app
from checkin.models import CheckIn
from meals.models import Meal, Eaten, MEAL_TYPE, ACTIVITIES
from meals.tables import MealsListTable, MealsListFilter, MealsUsersTable, MealsUsersFilter
from user.mixins import IsOrganizerMixin, IsVolunteerMixin


def organizer_tabs(user):
    if user.is_organizer:
        return [('Meals', reverse('meals_list'), False),
                ('Users', reverse('meals_users'), False),
                ('Activities', reverse('activity_list'), False),
                ('Activity users', reverse('activity_users'), False)]
    return [('Meals', reverse('meals_list'), False), ('Activities', reverse('activity_list'), False),]


class MealsList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_list.html'
    table_class = MealsListTable
    filterset_class = MealsListFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        queryset = Meal.objects.exclude(kind__in=ACTIVITIES)
        if not self.request.user.is_organizer:
            queryset = queryset.filter(opened=True)
        return queryset


class ActivitiesList(MealsList):
    def get_queryset(self):
        queryset = Meal.objects.filter(kind__in=ACTIVITIES)
        if not self.request.user.is_organizer:
            queryset = queryset.filter(opened=True)
        return queryset


class MealsUsers(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_users.html'
    table_class = MealsUsersTable
    filterset_class = MealsUsersFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Eaten.objects.exclude(meal__kind__in=ACTIVITIES)


class ActivitiesUsers(MealsUsers):
    def get_queryset(self):
        return Eaten.objects.filter(meal__kind__in=ACTIVITIES)


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
        mealopened = request.POST.get('meal_opened')
        meal.opened = (mealopened == 'opened')
        meal.save()
        messages.success(self.request, 'Meal updated!')
        return redirect('activity_list' if meal.kind in ACTIVITIES else 'meals_list')


class MealAdd(IsOrganizerMixin, TabsView):
    template_name = 'meal_add.html'

    def get_back_url(self):
        return reverse('meals_list')

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
        mealopened = request.POST.get('meal_opened')
        if mealopened:
            meal.opened = (mealopened == 'opened')
        meal.save()
        messages.success(self.request, 'Meal added!')
        return redirect('activity_list' if meal.kind in ACTIVITIES else 'meals_list')


class MealsCheckin(IsVolunteerMixin, TemplateView):
    template_name = 'meal_checkin.html'

    def get_context_data(self, **kwargs):
        context = super(MealsCheckin, self).get_context_data(**kwargs)
        mealid = kwargs['id']
        meal = Meal.objects.filter(id=mealid).first()
        if not meal:
            raise Http404

        if not meal.opened and not self.request.user.is_organizer:
            raise PermissionDenied('Meal is not active')

        context.update({
            'meal': meal,
            'back': 'meals_list' if not meal.activity() else 'activity_list'
        })
        if self.request.GET.get('success', False):
            context.update({
                'success': True,
                'diet': self.request.GET.get('diet', False)
            })
        if self.request.GET.get('error', False):
            context.update({
                'error': self.request.GET.get('error', 'Seems there\'s an error'),
            })
        return context


class MealsCoolAPI(View, IsVolunteerMixin):

    def post(self, request, *args, **kwargs):
        mealid = request.POST.get('meal_id', None)
        qrid = request.POST.get('qr_id', None)

        if not qrid or not mealid:
            return JsonResponse({'error': 'Missing meal and/or QR. Trying to trick us?', 'success': False})

        current_meal = Meal.objects.filter(id=mealid).first()
        if not current_meal.opened and not self.request.user.is_organizer:
            return JsonResponse({'error': 'Meal has been closed. Reach out to an organizer to activate it again',
                                 'success': False})
        hacker_checkin = CheckIn.objects.filter(qr_identifier=qrid).first()
        if not hacker_checkin:
            return JsonResponse({'error': 'Invalid QR code!', 'success': False})

        hacker_application = hacker_checkin.application
        if not hacker_application:
            return JsonResponse({'error': 'No application found for current code', 'success': False})

        times_hacker_ate = Eaten.objects.filter(meal=current_meal, user=hacker_application.user).count()
        if times_hacker_ate >= current_meal.times:
            error_message = 'Warning! Hacker already ate %d out of %d available times!' % \
                            (times_hacker_ate, current_meal.times)

            return JsonResponse({'error': error_message, 'success': False})

        checkin = Eaten(meal=current_meal, user=hacker_application.user)
        checkin.save()

        if hacker_application.diet == models_app.D_NONE:
            diet = 'No dietary restriction.'
        elif hacker_application.diet == models_app.D_OTHER:
            diet = hacker_application.other_diet
        else:
            diet = hacker_application.diet

        return JsonResponse({'diet': diet, 'success': True})
