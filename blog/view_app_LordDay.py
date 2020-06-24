
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
        # return HttpResponse("Hello, world. You're at the polls index.")
        # from api.serializers import SermonSerializer4API, MediaSerializer4API
        # from churchs.models import Media
        # from django.db.models import Prefetch
        # # queryset=Sermon.objects.all()

        chs = Church.objects.filter(code='ims')

        # theLogger.info('user:%s' % request.user)
        theLogger.info('church:%s' % chs[0])
        # theLogger.info('Lord Day:%s' % request.user.church.Lord_Day_column)
        
        # ccol = ContentColumn.objects.get(id=pk)
        CColsz = CColSerializer(chs[0].Lord_Day_column)
        # ccolDict = {
        #    'data':CColsz.data
        # }
        banners = chs[0].Lord_Day_swipe.all()
        theLogger.info('----------banners:')
        theLogger.info(banners)
        if banners:
            banners = MediaSerializer4ListAPI(banners,many=True)
        template = loader.get_template('blog/ccol.html')
        context = {
            'ccol': CColsz.data,
            'banners':banners.data
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e