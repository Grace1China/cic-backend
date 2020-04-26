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
import json

def browse(request):
    try:
        typ = request.GET["type"]
        res_path = SermonSeries.objects.filter(church=request.user.church).values('res_path','title')
        ls_res_path = list(res_path)
        path = ls_res_path[0]['res_path'] if len(ls_res_path)>0 else '/'  #默认显示根目录的文件 同专栏系列的默认设置保持一致
        files = _list_img(request.user,typ='images',path=path,marker='')
        sereis_dict = dict()
        for i in ls_res_path:
            sereis_dict[i['res_path']] = i['title']
    
        from api.alioss_directup_views import AliOssSignature
        token = AliOssSignature.cls_get_token(request.user.church.code)#这个参数有还要在此方法内加入校验。
        lg.info(token)

        # {"accessid": "LTAI4Fd1JMHM3WSUN4vrHcj8", "host": "https://bicf-media-source.oss-accelerate.aliyuncs.com", "desthost": "https://bicf-media-destination.oss-accelerate.aliyuncs.com", "policy": "eyJleHBpcmF0aW9uIjogIjIwMjAtMDQtMThUMDc6NDc6NDlaIiwgImNvbmRpdGlvbnMiOiBbWyJzdGFydHMtd2l0aCIsICIka2V5IiwgIkwzIl1dfQ==", "signature": "cnmgjhxg5wo65PuGU58/UlT/7No=", "expire": 1587196069, "dir": "L3/", "callback": "eyJjYWxsYmFja1VybCI6ICJodHRwOi8vdGVzdC5sMy5iaWNmLm9yZy9yYXBpL2FsaW9zc19kaXJlY3R1cF9jYWxsYmFjayIsICJjYWxsYmFja0JvZHkiOiAiZmlsZW5hbWU9JHtvYmplY3R9JnNpemU9JHtzaXplfSZtaW1lVHlwZT0ke21pbWVUeXBlfSZoZWlnaHQ9JHtpbWFnZUluZm8uaGVpZ2h0fSZ3aWR0aD0ke2ltYWdlSW5mby53aWR0aH0iLCAiY2FsbGJhY2tCb2R5VHlwZSI6ICJhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQifQ=="}

        context = {
            'show_dirs': True,#这个可能没有什么用发，目前留着
            'series': sereis_dict,
            'files': files,
            'form': None ,#form
            'MEDIA_BROWSE_API_SERVER':settings.MEDIA_BROWSE_API_SERVER, #就是首次加载图片的地址，为了实现本地调试sandbox的api,但在sandbox和product中用的各自外网地址
            'rediret_url_prefix':settings.ALIOSS_DESTINATIONS[typ]['redirecturl'],#跨国的redirect 是国内外的nginx配置，参考设计文档
            'OSSAccessKeyId': token['accessid'],
            'policy': token['policy'],
            'Signature': token['signature'],
            'callback': token['callback'],
            'type':typ,
            'churchcode':request.user.church.code,

        }
        lg.info(context)
        return render(request, 'church/media_browse.html', context)
    except Exception as e:
        import traceback
        import sys
        ret = {'errCode': '1001', 'msg': 'there is an exception check err logs','sysErrMsg':traceback.format_exc()}
        lg.exception('There is and exceptin',exc_info=True,stack_info=True)
        return render(request, 'exception.html', ret)
    
    



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
            page = data.get('page',1)
            series = data.get('series','/') #默认的专栏，这样在专栏生成前应该有一个预置的默认专栏。就是用这个根目录。
            
            # path = '%s%s' % (storage._get_user_path(request.user), '' if path=='' else '/'+path) #教会的目录是本函数负责加上
            if series != '':
                # files = _list_img(request.user,typ=typ,path=path,marker=marker)
                files,dirs = storage.get_files_from_db(user=request.user,typ=typ,series=series,page=page)
                ret = {'errCode': '0','msg':'success','data':files}
            else:
                raise Exception('series key must not null.')   
    except Exception as e:
        import traceback
        import sys
        ret = {'errCode': '1001', 'msg': 'there is an exception check err logs','sysErrMsg':traceback.format_exc()}
        lg.exception('There is and exceptin',exc_info=True,stack_info=True)
    finally:
        return JsonResponse(ret, safe=False)

def _list_img(user,typ=None,path='',marker=''):
    files,dirs = storage.get_files_browse_urls(user,typ,path,marker)
    return files





