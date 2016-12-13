import json
from logging import error

import requests
from django.conf import settings
from register import models

typeform_key = settings.REGISTER_APP['typeform_key']


class ApplicationFormFetcher(object):
    def incremental_fetch(self):
        raise NotImplemented

    def fetch(self):
        raise NotImplemented

    def map(self, obj):
        raise NotImplemented

    def save(self, application):
        raise NotImplemented

    def update_forms(self):
        forms = self.fetch()
        applications = map(self.map, forms)
        return map(self.save, applications)


class TypeformFetcher(ApplicationFormFetcher):
    base_url = 'https://api.typeform.com/v1/form/'

    def get_form_id(self):
        return settings.REGISTER_APP['applications_form_id']

    @property
    def url(self):
        return self.base_url + self.get_form_id()

    def fetch(self):
        resp = requests.get(self.url, params={'key': typeform_key, 'completed': 'true'})
        if resp.status_code != 200:
            error('The API responded with {}, status code:' + resp.status_code)
            return []
        return json.loads(resp.text)['responses']

    def save(self, application):
        application.save()

    def map(self, obj):
        a = models.Application()
        a.id = obj['token']
        answers = obj['answers']
        a.name = answers['textfield_28227510']
        a.lastname = answers['textfield_28227511']
        a.email = answers['email_28227516']
        a.authorized_mlh = answers['yesno_28227523']
        return a
