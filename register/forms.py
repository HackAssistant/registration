import json
from logging import error

import requests
from django.conf import settings
from register import models

typeform_key = settings.REGISTER_APP['typeform_key']


class ApplicationFormFetcher(object):
    def fetch(self):
        """
        Fetches data from external form
        :return: List of python objects
        """
        raise NotImplemented

    def load(self, obj):
        """
        Given a python object load to model
        :param obj: python object obtained from from
        :return: Model object populated by information from obj
        """
        raise NotImplemented

    def update_forms(self):
        """
        Outside method. Loads all data, loads to models and saves them
        :return: List n None, where n is the number of objects saved to the database
        """
        forms = self.fetch()
        if not forms:
            return []
        applications = map(self.load, forms)
        return [app.save() for app in applications]


class TypeformFetcher(ApplicationFormFetcher):
    """
    Base class for Typeform fetching
    """
    base_url = 'https://api.typeform.com/v1/form/'

    @property
    def form_id(self):
        """
        Obtain typeform form id
        :return: typeform form id
        """
        raise NotImplemented

    @property
    def url(self):
        """
        Generates API endpoint url from base_url and id
        :return: Typeform endpoint url for actual form
        """
        return self.base_url + self.form_id

    def fetch(self):
        resp = requests.get(self.url, params={'key': typeform_key, 'completed': 'true', 'offset': self.get_offset()})
        if resp.status_code != 200:
            error('The API responded with {}, status code:' + str(resp.status_code))
            return []
        return json.loads(resp.text)['responses']

    def load(self, obj):
        a = self.get_model()()
        a.id = obj['token']
        a.submission_date = obj['metadata']['date_submit']
        for k, f in self.get_map_dict().items():
            try:
                setattr(a, k, f(obj['answers']))
            except KeyError:
                pass
        return a

    def get_model(self):
        """
        defines model used
        :return: Model class
        """
        raise NotImplemented

    def get_map_dict(self):
        """
        Defines dictionary to map object attributes to model attributes
        :return:
        """
        raise NotImplemented

    def get_offset(self):
        return self.get_model().objects.count()


class ApplicationsTypeform(TypeformFetcher):
    def get_model(self):
        return models.Application

    def get_map_dict(self):
        return {
            'name': lambda x: x['textfield_37466587'],
            'lastname': lambda x: x['textfield_37466588'],
            'email': lambda x: x['email_37466593'],
            'graduation': lambda x: x['date_37466596'],
            'university': lambda x: x['dropdown_39151252'] if x['dropdown_39151252'] != 'Other' else x[
                'textfield_37466589'],
            'linkedin': lambda x: x['website_37466604'],
            'tshirt_size': lambda x: x['list_37466609_choice'],
            'degree': lambda x: x['dropdown_37466594'],
            'github': lambda x: x['website_37466602'],
            'devpost': lambda x: x['website_37466603'],
            'site': lambda x: x['website_37466605'],
            'first_timer': lambda x: x['yesno_37466598'],
            'team':lambda x:x['yesno_37466600'],
            'lennyface':lambda x:x['textfield_37466591'],
            'under_age': lambda x: x['yesno_37466597'],
            'description': lambda x: x['textarea_37466606'],
            'projects': lambda x: x['textarea_37466607'],
            'diet': lambda x: x['list_37466610_choice'],
            'country': lambda x: x['dropdown_37466595'],
            'teammates': lambda x: x['textarea_37466608'],
            'scholarship': lambda x: x['yesno_37466599'],
            'authorized_mlh': lambda x: x['yesno_37466601'],
        }

    @property
    def form_id(self):
        return 'JCVBqv'
