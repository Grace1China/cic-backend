from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from church.alioss_storage_backends_v3 import AliyunMediaStorage


# Create your views here.
import logging
theLogger = logging.getLogger('church.all')

def index(request,pk=0):
    # return HttpResponse("Hello, world. You're at the polls index.")
    from churchs.models import Sermon
    from api.serializers import SermonSerializer4API, MediaSerializer4API
    from churchs.models import Media
    from django.db.models import Prefetch
    # queryset=Sermon.objects.all()
    queryset = Sermon.objects.prefetch_related(Prefetch('medias',queryset=Media.objects.order_by('kind')))

    sm = queryset.get(id=pk)
    theLogger.info(sm)
    sz = SermonSerializer4API(sm)
    theLogger.info(sz.data)
    sermoninfo = sz.data['medias'][0]['content']
    template = loader.get_template('blog/premote.html')
    context = {
        'sermoninfo': sermoninfo,
    }
    return HttpResponse(template.render(context, request))


def tuwen(request,pk=0):
    try:
        # return HttpResponse("Hello, world. You're at the polls index.")
        from churchs.models import WeeklyReport
        # from api.serializers import SermonSerializer4API, MediaSerializer4API
        # from churchs.models import Media
        # from django.db.models import Prefetch
        # # queryset=Sermon.objects.all()
        tuwen = WeeklyReport.objects.get(id=pk)

        tuwenDict = {
            'image':AliyunMediaStorage.get_media_url('images', tuwen.image),
            'title':tuwen.title,
            'content':tuwen.content
        }
        template = loader.get_template('blog/tuwen.html')
        context = {
            'tuwen': tuwenDict,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e
from church.confs.base import get_ALIOSS_DESTINATIONS

def media(request,pk=0):
    try:
        # return HttpResponse("Hello, world. You're at the polls index.")
        from churchs.models import Media
        
        media = Media.objects.get(id=pk)

        media.hits = media.hits+1
        media.save()
        
        mediaDict = {
            'image':media.alioss_image,
            'title':media.title,
            'content':media.content,
            'kind':media.kind,
            'cover':'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ='images')['redirecturl'],media.alioss_image),
            'video':'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ='videos')['redirecturl'],media.alioss_video),
            'audio':media.alioss_audio,
        }
        template = loader.get_template('blog/media.html')
        context = {
            'media': mediaDict,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e


from rest_framework import serializers
from churchs.models import ContentColumn,Media
from api.serializers import MediaSerializer4ListAPI
class CColSerializer(serializers.ModelSerializer):
    medias = MediaSerializer4ListAPI(many=True, read_only=True)
    class Meta:
        model = ContentColumn
        fields = '__all__'

class MediasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

def column_content_medias(request,pk=0):
    try:
        # return HttpResponse("Hello, world. You're at the polls index.")
        # from api.serializers import SermonSerializer4API, MediaSerializer4API
        # from churchs.models import Media
        # from django.db.models import Prefetch
        # # queryset=Sermon.objects.all()
        ccol = ContentColumn.objects.get(id=pk)
        CColsz = CColSerializer(ccol)
        # ccolDict = {
        #    'data':CColsz.data
        # }
        template = loader.get_template('blog/ccol.html')
        context = {
            'ccol': CColsz.data,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e


      