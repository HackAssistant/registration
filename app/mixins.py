from django.forms import model_to_dict


class TabsViewMixin(object):
    def get_current_tabs(self):
        return []

    def get_back_url(self):
        return None

    def get_context_data(self, **kwargs):
        c = super(TabsViewMixin, self).get_context_data(**kwargs)
        c.update({'tabs': self.get_current_tabs(), 'back': self.get_back_url()})
        return c


class OverwriteOnlyModelFormMixin(object):
    '''
    Delete POST keys that were not actually found in the POST dict
    to prevent accidental overwriting of fields due to missing POST data.
    Based on:
     https://yuji.wordpress.com/2013/03/12/django-prevent-modelform-from-updating-values-if-user-did-not-submit-them/
    '''

    def clean(self):
        cleaned_data = super(OverwriteOnlyModelFormMixin, self).clean()
        c_cl_data = cleaned_data.copy()
        for field in c_cl_data.keys():
            if self.prefix is not None:
                post_key = '-'.join((self.prefix, field))
            else:
                post_key = field

            if post_key not in list(self.data.keys()) + list(self.files.keys()):
                # value was not posted, thus it should not overwrite any data.
                del cleaned_data[field]

        # only overwrite keys that were actually submitted via POST.
        model_data = model_to_dict(self.instance)
        model_data.update(cleaned_data)
        return model_data
