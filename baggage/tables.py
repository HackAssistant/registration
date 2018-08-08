import django_filters
import django_tables2 as tables
from baggage.models import Item

class BaggageListTable(tables.Table):

    class Meta:
        model = Item
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['id']
        empty_text = 'No baggage items available'