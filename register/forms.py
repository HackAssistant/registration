from logging import info, error

import requests
from register import models


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
        form_id = getattr(self, 'form_id', None)
        assert form_id
        return form_id

    @property
    def url(self):
        return self.base_url + self.get_form_id()

    def fetch(self):
        resp = requests.get(self.url, params={'key': 'test'})
        if resp.status_code != 200:
            error('The API responded with {}, status code:' + resp.status_code)
            return []
        return resp.json()*

    def save(self, application):
        application.save()

    def map(self, obj):
        return models.Application()


def update_form():
    offset = models.Application.count()
    info("Getting more responses from typeform API")
    requests.get()

    apiurl = baseapiurl.format(apikey=apikey, formid=formid, offset=offset.value)
    info("Using \"%s\" as api url", apiurl)
    request = Request(apiurl)

    try:
        response = urlopen(request)
        info("Request successful")
        response_text = response.read()
        json_dict = json.loads(response_text)

        if ('status' in json_dict and json_dict['status'] == 403):
            error("The API responded with: {}", json_dict['message'])
        else:
            num_responses = json_dict['stats']['responses']['showing']
            info("Gathered %s new responses", num_responses)
            clean_data = generateCleanDict(json_dict)

            createApplications(clean_data)
            # Update offset
            offset.value = str(int(offset.value) + num_responses)
            db.session.commit()

    except URLError, e:
        error('Error accessing API')
