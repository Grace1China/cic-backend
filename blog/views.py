from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader


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
    template = loader.get_template('blog/index.html')
    context = {
        'sermoninfo': sermoninfo,
    }
    return HttpResponse(template.render(context, request))