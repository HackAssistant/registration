from register.models import Application
from rest_framework import serializers


class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'


