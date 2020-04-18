# -*- coding: UTF-8 -*-

import socket
import base64
import sys
import time
import datetime
import json
import hmac
from hashlib import sha1 as sha
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
import oss2
from rest_framework.decorators import api_view, authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
import logging

theLogger = logging.getLogger('church.all')
from .utill import CICUtill
# permission_classes=CICUtill.getPermissionClass()
class AliOssSignature(APIView):
    '''
    给aliyun oss直传提供签名
    '''
    # 请填写您的AccessKeyId。
    access_key_id = 'LTAI4Fd1JMHM3WSUN4vrHcj8'
    # 请填写您的AccessKeySecret。
    access_key_secret = 'pXfMGYs2xAjjWHSKVoIaDuAC5ze49I'
    # host的格式为 bucketname.endpoint ，请替换为您的真实信息。
    host = 'https://bicf-media-source.oss-accelerate.aliyuncs.com'#'http://bicf-media-source.oss-cn-beijing.aliyuncs.com' 
    desthost = 'https://bicf-media-destination.oss-accelerate.aliyuncs.com'#'http://bicf-media-destination.oss-cn-beijing.aliyuncs.com'
    # callback_url为 上传回调服务器的URL，请将下面的IP和Port配置为您自己的真实信息。
    callback_url = "http://%s/rapi/alioss_directup_callback" %  settings.ALIOSS_MEDIA_CALLBACK_SERVER
    # 用户上传文件时指定的前缀。
    # upload_dir = '%s' %
    expire_time = 30

    def get_datetime_prefix(self):
        return dt.strftime('%Y%m%d%H%M%S%f')
         

    def get_iso_8601(self,expire):
        gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
        gmt += 'Z'
        return gmt


    def get_token(self,request):
        try:
            #import logging
            #logger = logging.getLogger('church.all')
            
            now = int(time.time())
            expire_syncpoint = now + self.expire_time
            # expire_syncpoint = 1612345678
            expire = self.get_iso_8601(expire_syncpoint)

            policy_dict = {}
            policy_dict['expiration'] = expire
            condition_array = []
            array_item = []
            array_item.append('starts-with')
            array_item.append('$key')
            if (request.user.church == None):
                # import pprint
                # pprint.PrettyPrinter(6).pprint(request.user)
                raise Exception('user or church of user is null')
            array_item.append(request.user.church.code)
            condition_array.append(array_item)
            policy_dict['conditions'] = condition_array
            policy = json.dumps(policy_dict).strip()
            policy_encode = base64.b64encode(policy.encode())
            h = hmac.new(self.access_key_secret.encode(), policy_encode, sha)
            sign_result = base64.encodestring(h.digest()).strip()

            callback_dict = {}
            callback_dict['callbackUrl'] = self.callback_url
            callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
                                            '&height=${imageInfo.height}&width=${imageInfo.width}'
            callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'

            #import logging
            theLogger.info(callback_dict)
            callback_param = json.dumps(callback_dict).strip()
            base64_callback_body = base64.b64encode(callback_param.encode())

            token_dict = {}
            token_dict['accessid'] = self.access_key_id
            token_dict['host'] = self.host
            token_dict['desthost'] = self.desthost
            token_dict['policy'] = policy_encode.decode()
            token_dict['signature'] = sign_result.decode()
            token_dict['expire'] = expire_syncpoint
            # token_dict['datetime_prefix'] = self.get_datetime_prefix()
            # token_dict['x-oss-object-acl'] = settings.ALIOSS_DESTINATIONS[]

            if request.user.church == None:
                token_dict['dir'] = 'l3/'
            else:
                token_dict['dir'] = '%s/' % request.user.church.code


            token_dict['callback'] = base64_callback_body.decode()
            result = json.dumps(token_dict)
            return result
        except Exception as e:
            #import logging
            #logger = logging.getLogger('church.all')
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
        finally:
            pass



    # @permission_classes([CICUtill.getPermissionClass()])
    # @permission_classes([IsAuthenticated])
    from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
    @permission_classes([IsAdminUser])
    def get(self, request, *args, **kwargs):
        """
        启用 Get 调用处理逻辑
        :param server: Web HTTP Server 服务
        :return:
        """
        print("********************* do_GET ")
        token = self.get_token(request)
        return JsonResponse({'errCode': '0', 'token': token}, safe=False)

import pprint
from churchs.models import MediaFile
class AliOssCallBack(APIView):
    '''
    阿里上传完成视频后进行回写
    '''
    permission_classes = [AllowAny]
    # def get(self,request,*args,**kwargs):
    #     '''
    #     用post方法
    #     '''
    #     import logging
    #     logging.debug('-------------------in get ----------------------')
    #     auth = request.META.get('Authorization')
    #     logging.debug(auth)
    #     # if not request:
    #     #     return None
    #     logging.debug(request)
    #     logging.debug(args)
    #     logging.debug(kwargs)
    #     pprint.PrettyPrinter(4).pprint(request)
    #     pprint.PrettyPrinter(4).pprint(args)
    #     pprint.PrettyPrinter(4).pprint(kwargs)
    #     return JsonResponse({'String value': 'OK', 'Key': 'Status'}, safe=False)

    def post(self,request,*args,**kwargs):
        '''
        用post方法
        '''
        try:
            from .utill import CICUtill
            theLogger.info('--------------AliOssCallBack-----in post ----------------------')
            theLogger.info(request.META)

            auth = request.META.get('Authorization')
            theLogger.info(auth)
            theLogger.info(request)
            theLogger.info(request.headers)
            theLogger.info(request.POST)
            data = request.data
            ret_dict = {}
            ret_dict['filename'] = data.get('filename', '')
            ret_dict['mimeType'] = data.get('mimeType','')
            ret_dict['signedurl'] = CICUtill.signurl(key=ret_dict['filename'],whichbucket='source')
            ret_dict['String value'] = 'OK'
            ret_dict['Key'] = 'Status'
            theLogger.info(ret_dict)
            # theLogger.info(json.dumps(ret_dict))
            mfile = MediaFile.objects.create(name=ret_dict['filename'], mime_type=ret_dict['mimeType'])
            theLogger.info(mfile)
            # return Response(data=json.dumps(ret_dict,ensure_ascii=False),status=status.HTTP_200_OK)

            # retV =  HttpResponse(json.dumps(ret_dict,ensure_ascii=False),content_type="application/json,charset=utf-8")
            retV = JsonResponse({'Status':'OK'}, safe=True)
            theLogger.info(retV.__dict__) #print it
            return   retV

        except Exception as e:
            #import logging
            #logger = logging.getLogger('church.all')
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
        finally:
            return JsonResponse(None, safe=False) 



    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        theLogger.info(self)
        theLogger.info(self.__dict__)

        # theLogger.info(self.action)
        # if self.action == 'post':
        permission_classes = [AllowAny]
        # else:
        # permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class AliMtsCallBack(APIView):
    def post(self,request,*args,**kwargs):
        '''
        用post方法
        用原文件来定位media,
        用计算的方法，来求得目标文件，存储在相应的记录里面
        4、15 这个方法 目前不用了。直接用文件查找，看目标盘是否有文件了。
        '''
        import logging    
        import churchs.models as md
        import urllib

        logger = logging.getLogger('dev.error')
        logger.error('-------------------in post ----------------------')

        topic = json.loads(request.body)
        msg = json.loads(topic['Message'])
        logger.error(msg)

        if msg['MediaWorkflowExecution']['State'] != 'Completed':
            return Response(data='',status=status.HTTP_204_NO_CONTENT)

        Bucket = msg['MediaWorkflowExecution']['Input']['InputFile']['Bucket']
        Object = msg['MediaWorkflowExecution']['Input']['InputFile']['Object']
        Location = msg['MediaWorkflowExecution']['Input']['InputFile']['Location']

        key_arr = Object.split('/')
        filename_arr = key_arr[1].rsplit('.',1)

        quotedfn = urllib.parse.quote(filename_arr[0])

        alioss_video = '%s/%s.%s' % (key_arr[0],quotedfn,filename_arr[1])
        alioss_SHD_URL = '%s/%s/%s.%s' % (key_arr[0],'mp4-hd',filename_arr[0],'mp4')
        alioss_HD_URL = '%s/%s/%s.%s' % (key_arr[0],'mp4-sd',filename_arr[0],'mp4')
        alioss_SD_URL = '%s/%s/%s.%s' % (key_arr[0],'mp4-ld',filename_arr[0],'mp4')
        alioss_image = '%s/%s.%s' % (key_arr[0],filename_arr[0],'jpg')

        logger.error('alioss_video:%s \n alioss_SHD_URL:%s \n alioss_HD_URL:%s \n alioss_SD_URL:%s \n alioss_image:%s \n' % (alioss_video,alioss_SHD_URL,alioss_HD_URL,alioss_SD_URL,alioss_image))
        qrset = md.Media.objects.filter(alioss_video__iexact=alioss_video)
        
        logger.error(qrset)

        qrset.update(alioss_video_status=md.Media.STATUS_DISTRIBUTED,alioss_SHD_URL=alioss_SHD_URL,alioss_HD_URL=alioss_HD_URL,alioss_SD_URL=alioss_SD_URL,alioss_image=alioss_image)
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
        bucket.put_object_acl(alioss_image, oss2.OBJECT_ACL_PUBLIC_READ)
        bucket.put_object_acl(alioss_HD_URL, oss2.OBJECT_ACL_PUBLIC_READ)

        return Response(data='',status=status.HTTP_204_NO_CONTENT)

# from .utill import CICUtill

# @api_view(['GET'])
# @permission_classes([CICUtill.getPermissionClass()])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def oss_object_exists(request,key=''):
    ret = {'errCode': '0', 'msg': 'media exists'}
    try:
        if request.method == 'GET':
            # data = request.data
            # key = data.get('key', '')
            if key != '':
                auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
                bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
                if bucket.object_exists(key):
                    ret = {'errCode': '0', 'msg': 'media exists'}
                    # return JsonResponse({'errCode': '0', 'msg': 'media exists'}, safe=False)
                else:
                    ret = {'errCode': '1001', 'msg': 'media not exists'}
            else:
                ret = {'errCode': '1001', 'msg': 'there is an exception check logs'}
                raise Exception('key must not null.')   
    except Exception as e:
        import traceback
        import sys
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    finally:
        return JsonResponse(ret, safe=False)
         
        