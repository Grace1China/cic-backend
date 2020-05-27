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
      