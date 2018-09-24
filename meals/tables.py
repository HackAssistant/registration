import django_filters
import django_tables2 as tables
from meals.models import Meal, MEAL_TYPE
from django.db.models import Q


class MealsListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    type = django_filters.ChoiceFilter(label='Type', choices=MEAL_TYPE, empty_label='Any')

    def search_filter(self, queryset, name, value):
        return queryset.filter((Q(name__icontains=value) | Q(type__icontains=value)))

    class Meta:
        model = Meal
        fields = ['search', 'type']


class MealsListTable(tables.Table):
    details = tables.TemplateColumn(
        "<a href='{% url 'meal_detail' record.id %}'>Users list</a> ",
        verbose_name='Details', orderable=False)
    change = tables.TemplateColumn(
        "<a href='{% url 'meal_detail' record.id %}'>Modify meal</a> ",
        verbose_name='Change', orderable=False)
    eaten = tables.Column(accessor='eaten', verbose_name='Eaten')

    class Meta:
        model = Meal
        attrs = {'class': 'table table-hover'}
        template = 'templates/meals_list.html'
        fields = ['id', 'name', 'type', 'times', 'starts', 'ends', 'eaten']
        empty_text = 'No meals available'
        order_by = 'starts'
