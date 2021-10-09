from cas_server.auth import DjangoAuthUser

from user.models import User


class MyHackUPCAuthUser(DjangoAuthUser):

    def __init__(self, username):
        try:
            self.user = User.objects.get(email=username, email_verified=True)
        except User.DoesNotExist:
            pass
        super(DjangoAuthUser, self).__init__(username)

    def attributs(self):
        return {
            'email': self.user.email,
            'name': self.user.name,
            'type': self.user.type,
        }
