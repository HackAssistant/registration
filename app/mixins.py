class TabsViewMixin(object):
    def get_current_tabs(self):
        return []

    def get_back_url(self):
        return None

    def get_context_data(self, **kwargs):
        c = super(TabsViewMixin, self).get_context_data(**kwargs)
        c.update({'tabs': self.get_current_tabs(), 'back': self.get_back_url()})
        return c
