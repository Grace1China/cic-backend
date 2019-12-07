from rest_framework import serializers
from . import models 
class SermonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sermon
        fields = ['id', 'church', 'user', 'title', 'date', 'description','pdf','speaker','scripture','series','cover','worshipvideo','mcvideo','sermonvideo','givingvideo','status']
       