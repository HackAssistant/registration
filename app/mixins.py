from django.forms import model_to_dict


class TabsViewMixin(object):
    def get_current_tabs(self):
        return []

    def get_back_url(self):
        return None

    def get_context_data(self, **kwargs):
        c = super(TabsViewMixin, self).get_context_data(**kwargs)
        c.update({'tabs': self.get_current_tabs(), 'back': self.get_back_url(), 'form_method': 'post'})
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


class BootstrapFormMixin:

    # example: {'TITLE': {'fields': [{'name': 'FIELD_NAME', 'space': GRID_NUMBER},], 'description': 'DESCRIPTION'},}
    # UPPER LETTERS MUST BE CHANGED
    bootstrap_field_info = {}
    read_only = []

    def get_bootstrap_field_info(self):
        return self.bootstrap_field_info

    def set_read_only(self):
        for field in self.fields.values():
            field.disabled = True

    @property
    def is_read_only(self):
        for field in self.fields.values():
            if not field.disabled:
                return False
        return True

    @property
    def get_fields(self):
        result = self.get_bootstrap_field_info()
        for list_fields in result.values():
            sum = 0
            for field in list_fields.get('fields'):
                if sum + field.get('space') > 12:
                    sum = field.get('space')
                    field['new_row'] = True
                else:
                    sum += field.get('space')
                    field['new_row'] = False
                name = field.get('name')
                field.update({'field': self.fields.get(name).get_bound_field(self, name)})
        return result
