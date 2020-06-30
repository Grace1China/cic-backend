
from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from church.alioss_storage_backends_v3 import AliyunMediaStorage
# Create your views here.
import logging
theLogger = logging.getLogger('church.all')
from rest_framework import serializers
from churchs.models import ContentColumn,Media
from api.serializers import MediaSerializer4ListAPI
from church.models import Church

from rest_framework_simplejwt.state import token_backend
from users.models import CustomUser

from django.conf import settings


class CColSerializer(serializers.ModelSerializer):
    medias = MediaSerializer4ListAPI(many=True, read_only=True)
    class Meta:
        model = ContentColumn
        fields = '__all__'

class MediasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

def column_content_Lord_Day(request,pk=0):
    try:
        data = request.GET
        token = data.get('token','')
        chs = None
        if token == '':
            chs = Church.objects.get(code=settings.DEFAULT_CHURCH_CODE)
        else:
            token1 = token_backend.decode(token, verify=True)
        
            if token1 == None:
                raise Exception('Token invalid!')
            
            theLogger.info(token1)
            user = CustomUser.objects.get(id = token1['user_id'])
            if user == None:
                raise Exception('No such user invalid!')
            theLogger.info(user)

            chs = user.church
            
            if chs == None:
                raise Exception('User has no church')
            theLogger.info('church:%s' % chs)
        CColsz = CColSerializer(chs.Lord_Day_column)
        ccol_medias = MediaSerializer4ListAPI(chs.Lord_Day_column.medias_list(),many=True)
        theLogger.info('---------------column_content_Lord_Day-------------------')
        theLogger.info(CColsz.data)
        banners = chs.Lord_Day_swipe.all()
        theLogger.info('----------banners:')
        theLogger.info(banners)
        if banners:
            banners = MediaSerializer4ListAPI(banners,many=True)
        template = loader.get_template('blog/LordDay.html')
        context = {
            'ccol': CColsz.data,
            'ccol_medias':ccol_medias.data,
            'banners':banners.data
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e