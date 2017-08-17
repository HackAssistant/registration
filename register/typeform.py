from django.conf import settings

from app.typeform import TypeformFetcher
from register import models


class ApplicationsTypeform(TypeformFetcher):
    def map_to_model(self, application, obj):
        answers = obj['answers']
        hidden = obj['hidden']
        application.id = obj['token']
        application.submission_date = obj['metadata']['date_submit']
        application.first_timer = answers['yesno_ynIA']
        application.team = answers['yesno_ZWM2']
        application.lennyface = answers['textfield_PYDC']
        # This is the negation, we ask if they will be >18 or not.
        # we keep if they are <18
        application.under_age = answers['yesno_54492568'] == '0'
        application.description = answers['textarea_M8Rz']
        application.projects = answers['textarea_WFi7']
        application.origin_city = answers['textfield_vqO7']
        application.origin_country = answers['dropdown_tE7S']
        application.teammates = answers.get('textarea_pI5i', '')
        application.scholarship = answers['yesno_hlsY']
        application.resume = answers['fileupload_54496801']
        application.authorized_mlh = answers['yesno_ITOL']
        application.hacker_id = hidden['hacker_id']
        return application

    @property
    def form_id(self):
        return settings.REGISTER_APP.get('typeform_form', 'KaZTUa')

    def get_model(self):
        return models.Application

    def get_offset(self):
        return models.Application.objects.count()


class FullApplicationsTypeform(ApplicationsTypeform):

    def get_offset(self):
        return 0
