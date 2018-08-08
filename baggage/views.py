from django.core.urlresolvers import reverse
from app.mixins import TabsViewMixin
from django.views.generic import TemplateView
from baggage.tables import BaggageListTable
from baggage.models import Item

def organizer_tabs(user):
    t = [('Check-in', reverse('baggage_list'), False)]
    return t

class BaggageList(TabsViewMixin, TemplateView):
    template_name = 'baggage_list.html'
    table_class = BaggageListTable
    table_pagination = {'per_page': 100}
  
    def get_current_tabs(self):
        return organizer_tabs(self.request.user)
    
    def get_queryset(self):
        return Item.objects.all()
      
    def get(self, request, *args, **kwargs):
         data = Item.objects.all()
         context = self.get_context_data(**kwargs)
         context['baggage_list'] = data
         return self.render_to_response(context)