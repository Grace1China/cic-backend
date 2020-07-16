
from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from church.alioss_storage_backends_v3 import AliyunMediaStorage
# Create your views here.
import logging
theLogger = logging.getLogger('church.all')
from rest_framework import serializers
from churchs.models.vpage import VPage
from churchs.models.vpage import VComponents 


from api.serializers import MediaSerializer4ListAPI
from church.models import Church

from rest_framework_simplejwt.state import token_backend
from users.models import CustomUser

from django.conf import settings


class VComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VComponents
        fields = '__all__'

class vpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPage
        fields = '__all__'

def vcomp(request,pk=0):
    try:
        data = request.GET
        id = data.get('componentid',0)
        vcomp = VComponents.objects.get(id=id)
        
        compsz = VComponentsSerializer(vcomp)
        template = loader.get_template('blog/vcomponents.html')
        context = {
            'vcomp': compsz.data,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e