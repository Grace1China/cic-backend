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
from oss2.models import Tagging, TaggingRule
from rest_framework.decorators import api_view, authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
import logging
from django.conf import settings
theLogger = logging.getLogger('church.all')
from .utill import CICUtill
from church.confs.base import get_ALIOSS_DESTINATIONS
import pprint
from churchs.models import MediaFile
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser


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
         
    @classmethod
    def get_iso_8601(self,expire):
        gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
        gmt += 'Z'
        return gmt


    
    @classmethod
    def cls_get_token(cls,object_prefix,typ='images'):
        '''
        因为一个教会所有用户共享目录，所以object_prefix就是church的根目录。根据阿里文档 需要以/结尾, 如L3/ L3/Series_1/
        '''
        try:
            #user_path = '' #因为不再用这个目录来区分文件，所以设置为空，但不影响原来的上下游代码
            theLogger.info('---------cls_get_token-----')
            now = int(time.time())
            expire_syncpoint = now + 30000
            # expire_syncpoint = 1612345678
            expire = AliOssSignature.get_iso_8601(expire_syncpoint)

            policy_dict = {}
            policy_dict['expiration'] = expire
            condition_array = []
            starts_array = []
            starts_array.append('starts-with')
            starts_array.append('$key')
            starts_array.append(object_prefix)
            condition_array.append({"bucket":get_ALIOSS_DESTINATIONS(typ)['bucket']})
            condition_array.append(starts_array)
            policy_dict['conditions'] = condition_array
            policy = json.dumps(policy_dict).strip()
            theLogger.info(policy)
            policy_encode = base64.b64encode(policy.encode())
            h = hmac.new(AliOssSignature.access_key_secret.encode(), policy_encode, sha)
            sign_result = base64.encodestring(h.digest()).strip()

            callback_dict = {}
            callback_dict['callbackUrl'] = AliOssSignature.callback_url
            callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
                                            '&height=${imageInfo.height}&width=${imageInfo.width}&originname=${x:originname}&dest=${x:dest}&seriesrespath=${x:seriesrespath}&church=${x:church}'
            callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'

            #import logging
            theLogger.info(callback_dict)
            callback_param = json.dumps(callback_dict).strip()
            base64_callback_body = base64.b64encode(callback_param.encode())

            token_dict = {}
            token_dict['accessid'] = AliOssSignature.access_key_id
            token_dict['host'] = AliOssSignature.host
            token_dict['desthost'] = AliOssSignature.desthost
            token_dict['policy'] = policy_encode.decode()
            token_dict['signature'] = sign_result.decode()
            token_dict['expire'] = expire_syncpoint
            # token_dict['datetime_prefix'] = self.get_datetime_prefix()
            # token_dict['x-oss-object-acl'] = settings.ALIOSS_DESTINATIONS[]

            token_dict['dir'] = '%s' % object_prefix
            token_dict['callback'] = base64_callback_body.decode()
            return token_dict

        except Exception as e:
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
            raise e
      


    def get_token(self,request):
        '''
        作为老方法保留
        '''
        try:
            #import logging
            #logger = logging.getLogger('church.all')
            
            now = int(time.time())
            expire_syncpoint = now + self.expire_time
            # expire_syncpoint = 1612345678
            expire = AliOssSignature.get_iso_8601(expire_syncpoint)

            policy_dict = {}
            policy_dict['expiration'] = expire
            condition_array = []
            array_item = []
            array_item.append('starts-with')
            array_item.append('$key')
            if (request.user.church == None):
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

    @permission_classes([IsAdminUser])
    def get(self, request, *args, **kwargs):
        """
        """
        ret = {'errCode': '1001', 'msg':'not complete','token': ''}
        try:
            if request.method == 'GET':
                token = self.get_token(request)
                ret = {'errCode': '0', 'msg':'success','token': token}
        except Exception as e:
            import traceback
            ret = {'errCode': '1001', 'msg': 'there is an exception check err logs','sysErrMsg':traceback.format_exc()}
            lg.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
        finally:
            return JsonResponse(ret, safe=False)


class AliOssSignatureV2(AliOssSignature):
    @permission_classes([IsAdminUser])
    def get(self, request, *args, **kwargs):
        """
        """
        ret = {'errCode': '1001', 'msg':'not complete','token': ''}
        try:
            if request.method == 'GET':
                data = request.GET
                typ = data.get('type','images')
                object_prefix = data.get('object_prefix','')

                token = AliOssSignature.cls_get_token(object_prefix,typ=typ)#现在存储结构，不按教会在物理上分了。只在数据库中分。是在回写中，带入了前端传入的教会名称。
                # AliOssSignature.cls_get_token(request.user.church.code,typ=typ)
                # token = self.get_token(request)
                ret = {'errCode': '0', 'msg':'success','token': token}
        except Exception as e:
            import traceback
            ret = {'errCode': '1001', 'msg': 'there is an exception check err logs','sysErrMsg':traceback.format_exc()}
            lg.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
        finally:
            return JsonResponse(ret, safe=False)
            
    @classmethod
    def cls_get_token(cls,object_prefix,typ='images'):
        return AliOssSignature.cls_get_token(object_prefix,typ=typ)


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
            theLogger.info(request.__dict__)
            theLogger.info(request.headers)
            theLogger.info(request.POST)
            data = request.data
            ret_dict = {}
            ret_dict['filename'] = data.get('filename', '')
            ret_dict['mimeType'] = data.get('mimeType','')
            if data.get('mimeType','').lower().find('mp4') >= 0 : #如果是mp4文件，要年原文件有没有， 其它类型都是在目标存储桶中
                ret_dict['signedurl'] = CICUtill.signurl(key=data.get('filename', ''),whichbucket='source')
            else:
                ret_dict['signedurl'] = CICUtill.signurl(key=data.get('filename', ''),whichbucket='destination')
            
            ret_dict['originname'] = data.get('originname','')


            ret_dict['Status'] = 'OK'
            theLogger.info(ret_dict)
            # aMediaFile = MediaFile.objects.filter(name=data.get('filename', ''))
            # key = data.get('filename', '')
            # if key:
            #     arrkey = key.split('/',1)
            
            mfile = MediaFile.objects.update_or_create(name=data.get('filename', ''),church_prefix=data.get('church',''),series_prefix=data.get('seriesrespath', ''),origin_name=data.get('originname',''), mime_type=data.get('mimeType',''),endpoint=get_ALIOSS_DESTINATIONS(data.get('dest', ''))['endpoint'],bucket=get_ALIOSS_DESTINATIONS(data.get('dest', ''))['bucket'])
            theLogger.info(mfile)

            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, get_ALIOSS_DESTINATIONS(data.get('dest', ''))['endpoint'], get_ALIOSS_DESTINATIONS(data.get('dest', ''))['bucket'])

            rule = TaggingRule()
            rule.add('originname', data.get('originname',''))
            rule.add('church', data.get('church',''))
            rule.add('series', data.get('seriesrespath',''))


            # 创建标签。
            tagging = Tagging(rule)

            # 设置标签。
            result = bucket.put_object_tagging(data.get('filename', ''), tagging)
            # 查看HTTP返回码。
            theLogger.info(' add tagging http response status:', result.status)

            retV = JsonResponse(ret_dict, safe=True)
            theLogger.info(retV.__dict__) #print it
            return   retV

        except Exception as e:
            #import logging
            #logger = logging.getLogger('church.all')
            theLogger.exception("there is an exception",exc_info=True,stack_info=True)
        # finally:
        #     return JsonResponse({'Status':'Cancel'}, safe=False) 



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
    permission_classes = [AllowAny]
    def post(self,request,*args,**kwargs):
        '''
        用原文件来定位media,
        用计算的方法，来求得目标文件，存储在相应的记录里面
        4、15 这个方法 目前不用了。直接用文件查找，看目标盘是否有文件了。
        --------------------------------------------------------------------
        04/25/2020 现在用这个prod环境 接收alioss的转码回调。但这个方法里不处理逻辑，而是往不同环境里发送执行逻辑请求。
        '''
        try:
            topic = json.loads(request.body)
            theLogger.info(topic)
            import urllib.request
            import urllib.parse
            data = urllib.parse.urlencode(topic)
            data = data.encode('ascii')

            theLogger.info(request.META)
            #request.META.HTTP_HOST 是ALIOSS MNS消息设置的地址。但由于只能设置一个地址，所以prod,sandbox都要用到这一个入口。再根据配置文件来选择要处理逻辑的服务器。还因为都布署在日本，所以他们访问的dns目标ip地址自然也就是日本的服务器。

            # ALIOSS_MEDIA_CALLBACK_SERVER_ENV['sandbox']
            # ALIOSS_MEDIA_CALLBACK_SERVER_ENV['prod']
            url1 = "http://%s/rapi/alioss_mts_finished_process" % settings.ALIOSS_MEDIA_CALLBACK_SERVER_ENV['sandbox']

            url2 = "http://%s/rapi/alioss_mts_finished_process" % settings.ALIOSS_MEDIA_CALLBACK_SERVER_ENV['prod']

            theLogger.info(url1)
            theLogger.info(url2)


            with urllib.request.urlopen(url1, data) as f:
                theLogger.info(f.read().decode('utf-8'))
            with urllib.request.urlopen(url2, data) as f:
                theLogger.info(f.read().decode('utf-8'))

        except Exception as e:
            import traceback
            ret = {'errCode': '1001', 'msg': 'there is an exception check logs','sysErrMsg':traceback.format_exc()}
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
        finally:
            return Response(data='',status=status.HTTP_204_NO_CONTENT)

class AliMtsCallBack_process(APIView):
    permission_classes = [AllowAny]
    def post(self,request,*args,**kwargs):
        '''
        逻辑处理
        '''
        import logging    
        import churchs.models as md
        import urllib
        try:

            theLogger.error('-------------------in post ----------------------')
            # {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'Act-Report', 'Type': 'Report', 'State': 'Success', 'MediaWorkflowExecution': {'MediaWorkflowId': 'cf66e7b257ef47d089c03b323a30840c', 'Name': 'base', 'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'MediaId': '2300c53ed1ab411fbca2f66519f153a2', 'Input': {'InputFile': {'Bucket': 'bicf-media-source', 'Location': 'oss-cn-beijing', 'Object': 'zgc/20200426ZGCENGM.mp4'}}, 'State': 'Completed', 'ActivityList': [{'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'Act-Report', 'Type': 'Report', 'State': 'Success', 'StartTime': '2020-04-26T03:08:10Z', 'EndTime': '2020-04-26T03:08:10Z'}, {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'Act-Start', 'Type': 'Start', 'JobId': 'eb27a74949eb43b9b5a472c10294eec6', 'State': 'Success', 'StartTime': '2020-04-26T02:56:21Z', 'EndTime': '2020-04-26T02:56:22Z'}, {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'base', 'Type': 'Snapshot', 'JobId': 'e2a2574e9db04ff7afab0a2c780f847c', 'State': 'Success', 'StartTime': '2020-04-26T02:56:22Z', 'EndTime': '2020-04-26T02:56:24Z'}, {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'HD', 'Type': 'Transcode', 'JobId': 'ba9cd39ad7ad47869044e47361ce6b45', 'TemplateId': 'S00000001-200030', 'State': 'Success', 'StartTime': '2020-04-26T02:56:22Z', 'EndTime': '2020-04-26T03:08:10Z'}, {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'LD', 'Type': 'Transcode', 'JobId': 'acf40e2037a642c78032b7f138366c3b', 'TemplateId': 'S00000001-200010', 'State': 'Success', 'StartTime': '2020-04-26T02:56:22Z', 'EndTime': '2020-04-26T03:01:44Z'}, {'RunId': '10ec94999fe441eaa665f2d7a509d4b5', 'Name': 'SD', 'Type': 'Transcode', 'JobId': '55ee0050ecfd4e09a840e7de09cdc760', 'TemplateId': 'S00000001-200020', 'State': 'Success', 'StartTime': '2020-04-26T02:56:22Z', 'EndTime': '2020-04-26T03:03:34Z'}], 'CreationTime': '2020-04-26T02:56:21Z', 'RequestId': '5EA4F7F0A15238BAA7390A40'}}
            topic = json.loads(request.body)
            theLogger.error(topic)
            msg = json.loads(topic['Message'])
            theLogger.error(msg)

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

            theLogger.error('alioss_video:%s \n alioss_SHD_URL:%s \n alioss_HD_URL:%s \n alioss_SD_URL:%s \n alioss_image:%s \n' % (alioss_video,alioss_SHD_URL,alioss_HD_URL,alioss_SD_URL,alioss_image))
            qrset = md.Media.objects.filter(alioss_video__iexact=alioss_video)

            
            theLogger.error(qrset)

            
            qrset.update(alioss_video_status=md.Media.STATUS_DISTRIBUTED,alioss_SHD_URL=alioss_SHD_URL,alioss_HD_URL=alioss_HD_URL,alioss_SD_URL=alioss_SD_URL,alioss_image=alioss_image)
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            bucket.put_object_acl(alioss_image, oss2.OBJECT_ACL_PUBLIC_READ)
            bucket.put_object_acl(alioss_HD_URL, oss2.OBJECT_ACL_PUBLIC_READ)
        except Exception as e:
            import traceback
            ret = {'errCode': '1001', 'msg': 'there is an exception check logs','sysErrMsg':traceback.format_exc()}
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
        finally:
            return Response(data='',status=status.HTTP_204_NO_CONTENT)

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
        ret = {'errCode': '1001', 'msg': 'there is an exception check logs','sysErrMsg':traceback.format_exc()}
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
        raise e
    finally:
        return JsonResponse(ret, safe=False)
         
        