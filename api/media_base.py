from rest_framework.decorators import api_view, authentication_classes,permission_classes
from django.http import HttpResponse, JsonResponse

from church.alioss_storage_backends_v3 import AliyunVideoStorage, AliyunMediaStorage
# from ImageUploadView import get_files_browse_urls
@api_view(['GET'])
def get_media(request):
    '''
    key是唯一定位的媒体，typ是为组织返回对像的结构
    '''
    ret = {'errCode': '0'}
    try:
        if request.method == 'GET':
            data = request.GET
            typ = data.get('typ','images')
            key = data.get('key','')
            ro = dict()#返回对像用来前端绑定
            if key != '':
                if typ == 'videos':
                    stg = AliyunVideoStorage()
                    ro = stg.get_media_from_db(user=request.user,typ=typ,key=key)
                else:
                    stg = AliyunMediaStorage()
                    ro = storage.get_media_from_db(user=request.user,typ=typ,key=key)
                ret = {'errCode': '0','msg':'success','data':ro}
            else:
                raise Exception(' key must not null.')   
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