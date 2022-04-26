import django_filters
import django_tables2 as tables

from checkin.models import CheckIn
from meals.models import Meal, MEAL_TYPE
from django.db.models import Q


class MealsListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    kind = django_filters.ChoiceFilter(label='Type', choices=MEAL_TYPE, empty_label='Any')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(name__icontains=value) | Q(type__icontains=value)))

    class Meta:
        model = Meal
        fields = ['search', 'kind']


class MealsListTable(tables.Table):
    change = tables.TemplateColumn(
        "<a href='{% url 'meal_detail' record.id %}'>Modify</a> ",
        verbose_name='Actions', orderable=False)
    checkin = tables.TemplateColumn(
        "<a href='{% url 'meal_checkin' record.id %}'>Check-in hacker</a> ",
        verbose_name='Check-in', orderable=False)
    starts = tables.DateColumn(accessor='starts', verbose_name='Starts', format='d/m G:i')
    ends = tables.DateTimeColumn(accessor='ends', verbose_name='Ends', format='d/m G:i')
    eaten = tables.Column(accessor='eaten', verbose_name='Total rations served')
    times = tables.Column(accessor='times', verbose_name='Rations/hacker')
    opened = tables.Column(accessor='opened', verbose_name='Active')

    def before_render(self, request):
        if not request.user.is_organizer:
            self.columns.hide('opened')
            self.columns.hide('change')
            self.columns.hide('ends')
            self.columns.hide('starts')

    class Meta:
        model = Meal
        attrs = {'class': 'table table-hover'}
        template = 'templates/meals_list.html'
        fields = ['name', 'kind', 'opened', 'eaten', 'times', 'starts', 'ends', ]
        empty_text = 'No meals available'
        order_by = '-starts'


class MealsUsersFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        try:
            checkin = CheckIn.objects.get(qr_identifier=value)
            return queryset.filter(user=checkin.application.user)
        except CheckIn.DoesNotExist:
            return queryset.filter(Q(meal__name__icontains=value) |
                                   Q(user__name__icontains=value) | Q(user__email__icontains=value))

    class Meta:
        model = Meal
        fields = ['search']


class MealsUsersTable(tables.Table):
    time2 = tables.DateTimeColumn(accessor='time', verbose_name='Time', format='d/m/Y G:i')

    class Meta:
        model = Meal
        attrs = {'class': 'table table-hover'}
        template = 'templates/meals_users.html'
        fields = ['id', 'meal', 'user', 'time2']
        empty_text = 'No hacker has eaten yet'
        order_by = 'time'
