from django.contrib.auth.models import User, Church
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone']


class ChurchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Church
        fields = ['name', 'time_desc', 'address']