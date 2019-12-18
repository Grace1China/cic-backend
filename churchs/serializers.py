from rest_framework import serializers
from . import models 
class SermonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sermon
        fields = ['id', 'church', 'user', 'title', 'date', 'description','pdf','speaker','scripture','series','cover','worshipvideo','mcvideo','sermonvideo','givingvideo','status']

class EweeklySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeeklyReport
        fields = ['id', 'church', 'creator', 'title', 'image','content','status','pub_time','create_time','update_time']
