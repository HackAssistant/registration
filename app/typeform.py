import json
import logging
from logging import error

import requests
from django.conf import settings

typeform_key = settings.REGISTER_APP['typeform_key']


class ApplicationFormFetcher(object):
    def _fetch(self):
        """
        Fetches data from external form
        :return: List of python objects
        """
        raise NotImplemented

    def _load(self, obj):
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
        forms = self._fetch()
        if not forms:
            return []
        applications = map(self._load, forms)
        return [app.save() for app in applications]

    def insert_forms(self):
        """
        Outside method. Loads all data, loads to models and saves them. If existing, only updates given fields
        :return: List n None, where n is the number of objects saved to the database
        """
        forms = self._fetch()
        if not forms:
            return []
        applications = map(self._load, forms)
        ret = []
        for app in applications:
            try:
                ret += [app.save(force_insert=True)]
            except Exception as e:
                logging.error(e.message)
                logging.error('Application failed to insert %s' % app.hacker_id)

        return ret


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

    def _fetch(self):
        resp = requests.get(self.url, params={'key': typeform_key, 'limit': '8000', 'completed': 'true',
                                              'offset': self.get_offset()})
        if resp.status_code != 200:
            error('The API responded with {}, status code:' + str(resp.status_code))
            return []
        return json.loads(resp.text)['responses']

    def _load(self, obj):
        a = self.get_model()()
        a = self.map_to_model(a, obj)
        return a

    def get_model(self):
        raise NotImplemented

    def map_to_model(self, model, obj):
        """
        Defines dictionary to map object attributes to model attributes
        :return:
        """
        raise NotImplemented

    def get_offset(self):
        return 0
