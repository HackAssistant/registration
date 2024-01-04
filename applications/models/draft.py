

from user.models import User, BlacklistUser
from user import models as userModels

from .base import *
class DraftApplication(models.Model):
    content = models.CharField(max_length=7000)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def save_dict(self, d):
        self.content = json.dumps(d)

    def get_dict(self):
        return json.loads(self.content)

    @staticmethod
    def create_draft_application(instance):
        dict = model_to_dict(instance)
        for key in ['user', 'invited_by', 'submission_date', 'status_update_date', 'status', 'resume']:
            dict.pop(key, None)
        d = DraftApplication()
        d.user_id = instance.user_id
        d.save_dict(dict)
        d.save()
