
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


class vpage_positionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VComponents
        fields = '__all__'

class vpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPage
        fields = '__all__'

def vpage(request,pk=0):
    try:
        data = request.GET
        id = data.get('vpage',0)
        avp = vpage_md.objects.get(id=id)
        avp_pos = avp.vpage_position_set.all()
        avp_sz = vpageSerializer(avp)
        avpos_sz = vpage_positionSerializer(avp_pos,many=True)
        template = loader.get_template('blog/vpage.html')
        context = {
            'vpage': avp_sz.data,
            'vpos':avpos_sz.data
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e