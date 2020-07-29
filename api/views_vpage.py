from rest_framework.decorators import api_view, authentication_classes,permission_classes
from churchs.models import *
from church.models import *
from api.models import *
from payment.models import *
# from .utill import CICUtill
from .utill import CICUtill
from urllib.parse import unquote

from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_ARRAY
from drf_yasg.utils import swagger_auto_schema
from django.db.models.fields import CharField
from churchs.models import Media
from rest_framework import serializers,viewsets
from rest_framework.decorators import action
from django.http import HttpResponse, JsonResponse
from .utill import timeSpan
from datetime import datetime as dd
from django.views.decorators.csrf import csrf_exempt

theLogger = logging.getLogger('church.all')

from churchs.models.vpage import VComponents, VParts
from itertools import islice



@api_view(['POST'])
def add_parts(request):
    '''
    添加Parts
    '''
    ret = {'errCode': '0'}
    try:
        if request.META['REQUEST_METHOD']  == 'POST':
            # data = request.POST
            theLogger.info('------------------add_parts------linkjsons')
            theLogger.info(request.data)
            data = request.data
            linkjsons = data.get('linkjsons','[]')
            linkjsons = json.loads(linkjsons)
            compid = data.get('compid',-1)
            theLogger.info('------------------add_parts------linkjsons:%s-----compid:%s----' % (json.dumps(linkjsons),compid))
            batch_size = len(linkjsons)
            objs = (VParts(components_id=compid,cover=lnjson['thumb'],title=lnjson['visible_filename'],url_obj=json.dumps(lnjson)) for lnjson in linkjsons)
            # theLogger.info()
            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                VParts.objects.bulk_create(batch, batch_size)
                
                # lnjson
                # VParts
                # VParts.objects.bulk_create([
                #     VParts(components=compid,cover=lnjson.cover,title=lnjson.title,url_obj=json.dumps(lnjson)),
                #     VParts(headline='This is only a test'),
                # ])

                # id = models.AutoField(pr
                # components = models.Fore
                # cover = models.CharField
                # title = models.CharField
                # url_obj = JSONField()
                # url = models.CharField(m
                # url_title = models.CharF
                # url_object = models.Char
                # url_id = models.IntegerF
                # css = models.CharField(m
                # order = models.PositiveS
                # VComponents.objects.get(id=compid)
                # VParts.objects.bulk_create()

            ret = {'errCode': '0','msg':'success'}

    except Exception as e:
        theLogger.info('There is an exceptin',exc_info=True,stack_info=True)
        ret = {'errCode': '1001', 'data': None,'msg':'There is an exceptin','sysErrMsg':traceback.format_exc()}
    finally:
        return JsonResponse(ret, safe=False)

@api_view(['POST'])
def delete_parts(request):
    '''
    添加Parts
    '''
    ret = {'errCode': '0'}
    try:
        if request.method == 'POST':
            data = request.POST
            partid = data.get('partid','-1')
            VParts.objects.get(id=partid).delete()
            ret = {'errCode': '0','msg':'success'}
    except Exception as e:
        theLogger.exception('There is an exceptin',exc_info=True,stack_info=True)
        ret = {'errCode': '1001', 'data': None,'msg':'There is an exceptin','sysErrMsg':traceback.format_exc()}
    finally:
        return JsonResponse(ret, safe=False)