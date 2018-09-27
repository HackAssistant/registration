import django_filters
import django_tables2 as tables
from meals.models import Meal, MEAL_TYPE
from django.db.models import Q


class MealsListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    type2 = django_filters.ChoiceFilter(label='Type', choices=MEAL_TYPE, empty_label='Any')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(name__icontains=value) | Q(type__icontains=value)))

    class Meta:
        model = Meal
        fields = ['search', 'type2']


class MealsListTable(tables.Table):
    change = tables.TemplateColumn(
        "<a href='{% url 'meal_detail' record.id %}'>Modify</a> ",
        verbose_name='Actions', orderable=False)
    starts2 = tables.DateColumn(accessor='starts', verbose_name='Starts', format='d/m/Y G:i')
    ends2 = tables.DateTimeColumn(accessor='ends', verbose_name='Ends', format='d/m/Y G:i')
    eaten = tables.Column(accessor='eaten', verbose_name='Eaten')

    class Meta:
        model = Meal
        attrs = {'class': 'table table-hover'}
        template = 'templates/meals_list.html'
        fields = ['id', 'name', 'kind', 'times', 'starts2', 'ends2', 'eaten']
        empty_text = 'No meals available'
        order_by = 'starts'


class MealsUsersFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(meal__name__icontains=value) | Q(user__name__icontains=value) |
                                Q(user__email__icontains=value)))

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
