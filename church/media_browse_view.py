from __future__ import absolute_import, unicode_literals

import inspect
import os
import warnings
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .alioss_storage_backends_v3 import AliyunMediaStorage
from .utils import storage


from .utils import is_valid_image_extension
import logging
lg = logging.getLogger('church.all')



from churchs.models import SermonSeries

def browse(request):
    typ = request.GET["type"]
    res_path = SermonSeries.objects.filter(church=request.user.church).values('res_path')
    ls_res_path = list(res_path)
    path = ls_res_path[0]['res_path'] if len(ls_res_path)>0 else '/'  #默认显示根目录的文件 同专栏系列的默认设置保持一致
    #files,dirs = storage.get_files_browse_urls(request.user,typ=typ,marker='')#not use dirs use res_path
    files = _list_img(request.user,typ='images',path=path,marker='')
    dirs = list()
    for i in ls_res_path:
        dirs.append(i['res_path'])
  
    from api.alioss_directup_views import AliOssSignature
    token = AliOssSignature.cls_get_token('L3')
    lg.info(token)

    # {"accessid": "LTAI4Fd1JMHM3WSUN4vrHcj8", "host": "https://bicf-media-source.oss-accelerate.aliyuncs.com", "desthost": "https://bicf-media-destination.oss-accelerate.aliyuncs.com", "policy": "eyJleHBpcmF0aW9uIjogIjIwMjAtMDQtMThUMDc6NDc6NDlaIiwgImNvbmRpdGlvbnMiOiBbWyJzdGFydHMtd2l0aCIsICIka2V5IiwgIkwzIl1dfQ==", "signature": "cnmgjhxg5wo65PuGU58/UlT/7No=", "expire": 1587196069, "dir": "L3/", "callback": "eyJjYWxsYmFja1VybCI6ICJodHRwOi8vdGVzdC5sMy5iaWNmLm9yZy9yYXBpL2FsaW9zc19kaXJlY3R1cF9jYWxsYmFjayIsICJjYWxsYmFja0JvZHkiOiAiZmlsZW5hbWU9JHtvYmplY3R9JnNpemU9JHtzaXplfSZtaW1lVHlwZT0ke21pbWVUeXBlfSZoZWlnaHQ9JHtpbWFnZUluZm8uaGVpZ2h0fSZ3aWR0aD0ke2ltYWdlSW5mby53aWR0aH0iLCAiY2FsbGJhY2tCb2R5VHlwZSI6ICJhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQifQ=="}

    context = {
        'show_dirs': True,
        'dirs': dirs,
        'files': files,
        'form': None ,#form
        'MEDIA_BROWSE_API_SERVER':settings.MEDIA_BROWSE_API_SERVER,
        'rediret_url_prefix':settings.ALIOSS_DESTINATIONS[typ]['redirecturl'],
        'OSSAccessKeyId': token['accessid'],
        'policy': token['policy'],
        'Signature': token['signature'],
        'callback': token['callback'],

    }
    lg.info(context)
    return render(request, 'church/media_browse.html', context)


# class Alioss_view(generic.View):
#     def list_dir(request):
#         # AliyunMediaStorage()
#         storage.listdir(browse_path)

from rest_framework.decorators import api_view, authentication_classes,permission_classes
from django.http import HttpResponse, JsonResponse
# from ImageUploadView import get_files_browse_urls
@api_view(['GET'])
def list_img(request,path=''):
    '''
    列出指定路径下的所有图片，这个path，应该是用户透明的。也就用户只知道系列的目录。然后教会的目录是本函数负责加上
    '''
    lg.info(path)
    ret = {'errCode': '0'}
    try:
        if request.method == 'GET':
            data = request.GET
            typ = data.get('type','images')
            marker = data.get('marker','')
            path = '%s%s' % (storage._get_user_path(request.user), '' if path=='' else '/'+path) #教会的目录是本函数负责加上
            if path != '':
                files = _list_img(request.user,typ=typ,path=path,marker=marker)
                # files,dirs = storage.get_files_browse_urls(request.user,typ,path,marker)
                ret = {'errCode': '0','msg':'success','data':files}
            else:
                raise Exception('key must not null.')   
    except Exception as e:
        import traceback
        import sys
        ret = {'errCode': '1001', 'msg': 'there is an exception check err logs'}
        lg.exception('There is and exceptin',exc_info=True,stack_info=True)
    finally:
        return JsonResponse(ret, safe=False)

def _list_img(user,typ=None,path='',marker=''):
    files,dirs = storage.get_files_browse_urls(user,typ,path,marker)
    return files





