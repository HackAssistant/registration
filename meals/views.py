import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.core.serializers.python import Serializer
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from app.mixins import TabsViewMixin
from app.views import TabsView
from applications import models as models_app
from checkin.models import CheckIn
from meals.models import Meal, Eaten, MEAL_TYPE
from meals.tables import MealsListTable, MealsListFilter, MealsUsersTable, MealsUsersFilter
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
        if self.request.user.is_organizer:
            return Meal.objects.all()
        return Meal.objects.filter(opened=True)


class MealsUsers(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'meals_users.html'
    table_class = MealsUsersTable
    filterset_class = MealsUsersFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Eaten.objects.all()


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
        return redirect('meals_list')


class MealAdd(IsOrganizerMixin, TabsView):
    template_name = 'meal_add.html'

    def get_back_url(self):
        return redirect('meals_list')

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
        return redirect('meals_list')


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
            return JsonResponse({'error': 'Missing meal and/or QR. Trying to trick us?'})

        current_meal = Meal.objects.filter(id=mealid).first()
        if not current_meal.opened and not self.request.user.is_organizer:
            return JsonResponse({'error': 'Meal has been closed. Reach out to an organizer to activate it again'})
        hacker_checkin = CheckIn.objects.filter(qr_identifier=qrid).first()
        if not hacker_checkin:
            return JsonResponse({'error': 'Invalid QR code!'})

        hacker_application = getattr(hacker_checkin, 'application', None)
        if not hacker_application:
            return JsonResponse({'error': 'No application found for current code'})

        times_hacker_ate = Eaten.objects.filter(meal=current_meal, user=hacker_application.user).count()
        if times_hacker_ate >= current_meal.times:
            error_message = 'Warning! Hacker already ate %d out of %d available times!' % \
                            (times_hacker_ate, current_meal.times)

            return JsonResponse({'error': error_message})

        checkin = Eaten(meal=current_meal, user=hacker_application.user)
        checkin.save()

        if hacker_application.diet == models_app.D_NONE:
            diet = 'No dietary restriction.'
        elif hacker_application.diet == models_app.D_OTHER:
            diet = hacker_application.other_diet
        else:
            diet = hacker_application.diet

        return JsonResponse({'success': True, 'diet': diet})


class MealSerializer(Serializer):
    def end_object(self, obj):
        self._current['id'] = obj._get_pk_val()
        self._current['starts'] = str(obj.starts)
        self._current['ends'] = str(obj.ends)
        self._current['kind'] = obj.get_kind_display()
        self._current['eaten'] = obj.eaten()
        self.objects.append(self._current)


class MealsApi(APIView):
    permission_classes = (AllowAny,)

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
        serializer = MealSerializer()
        meals_data = serializer.serialize(meals)
        print(meals_data)
        return HttpResponse(json.dumps({'code': 0, 'content': meals_data}), content_type='application/json')

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
            if obj_user.diet:
                var_diet = obj_user.diet
            else:
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
