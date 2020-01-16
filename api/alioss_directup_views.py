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



class AliOssSignature(APIView):
    '''
    给aliyun oss直传提供签名
    '''
    # 请填写您的AccessKeyId。
    access_key_id = 'LTAI4Fd1JMHM3WSUN4vrHcj8'
    # 请填写您的AccessKeySecret。
    access_key_secret = 'pXfMGYs2xAjjWHSKVoIaDuAC5ze49I'
    # host的格式为 bucketname.endpoint ，请替换为您的真实信息。
    host = 'http://bicf-media-source.oss-cn-beijing.aliyuncs.com' 
    desthost = 'http://bicf-media-destination.oss-cn-beijing.aliyuncs.com'
    # callback_url为 上传回调服务器的URL，请将下面的IP和Port配置为您自己的真实信息。
    callback_url = "http://%s/rapi/alioss_directup_callback" %  settings.APP_SERVER_IP
    # 用户上传文件时指定的前缀。
    # upload_dir = '%s' %
    expire_time = 30


    def get_iso_8601(self,expire):
        gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
        gmt += 'Z'
        return gmt


    def get_token(self,request):
        now = int(time.time())
        expire_syncpoint = now + self.expire_time
        # expire_syncpoint = 1612345678
        expire = self.get_iso_8601(expire_syncpoint)

        policy_dict = {}
        policy_dict['expiration'] = expire
        condition_array = []
        array_item = []
        array_item.append('starts-with');
        array_item.append('$key');
        if (request.user.church == None):
            import pprint
            pprint.PrettyPrinter(6).pprint(request.user)
            raise Exception('user or church of user is null')
        array_item.append(request.user.church.code);
        condition_array.append(array_item)
        policy_dict['conditions'] = condition_array
        policy = json.dumps(policy_dict).strip()
        policy_encode = base64.b64encode(policy.encode())
        h = hmac.new(self.access_key_secret.encode(), policy_encode, sha)
        sign_result = base64.encodestring(h.digest()).strip()

        callback_dict = {}
        callback_dict['callbackUrl'] = self.callback_url;
        callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
                                        '&height=${imageInfo.height}&width=${imageInfo.width}';
        callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded';
        import logging
        logging.debug(callback_dict)
        callback_param = json.dumps(callback_dict).strip()
        base64_callback_body = base64.b64encode(callback_param.encode());

        token_dict = {}
        token_dict['accessid'] = self.access_key_id
        token_dict['host'] = self.host
        token_dict['desthost'] = self.desthost
        token_dict['policy'] = policy_encode.decode()
        token_dict['signature'] = sign_result.decode()
        token_dict['expire'] = expire_syncpoint

        if request.user.church == None:
            token_dict['dir'] = 'l3/'
        else:
            token_dict['dir'] = '%s/' % request.user.church.code



        token_dict['callback'] = base64_callback_body.decode()
        result = json.dumps(token_dict)
        return result




    def get(self, request, *args, **kwargs):
        """
        启用 Get 调用处理逻辑
        :param server: Web HTTP Server 服务
        :return:
        """
        print("********************* do_GET ")

        token = self.get_token(request)
        # server.send_response(200)
        # server.send_header('Access-Control-Allow-Methods', 'POST')
        # server.send_header('Access-Control-Allow-Origin', '*')
        # server.send_header('Content-Type', 'text/html; charset=UTF-8')
        # server.end_headers()
        # server.wfile.write(token.encode())
        return JsonResponse({'errCode': '0', 'token': token}, safe=False)


import pprint
class AliOssCallBack(APIView):
    '''
    阿里上传完成视频后进行回写
    '''
    def get(self,request,*args,**kwargs):
        '''
        用post方法
        '''
        import logging
        logging.debug('-------------------in get ----------------------')
        auth = request.META.get('Authorization')
        logging.debug(auth)
        # if not request:
        #     return None
        logging.debug(request)
        logging.debug(args)
        logging.debug(kwargs)
        pprint.PrettyPrinter(4).pprint(request)
        pprint.PrettyPrinter(4).pprint(args)
        pprint.PrettyPrinter(4).pprint(kwargs)
        return JsonResponse({'String value': 'OK', 'Key': 'Status'}, safe=False)

    def post(self,request,*args,**kwargs):
        '''
        用post方法
        '''
        import oss2
        import logging
        
        logger = logging.getLogger('dev.error')
        logger.error('-------------------in post ----------------------')

        auth = request.META.get('Authorization')
        logger.error(auth)
        # if not request:
        #     return None
        logger.error(request)
        logger.error(request.headers)
        # X-Oss-Bucket
        logger.error(request.POST)
        data = request.data
        filename = data.get('filename', '')
        mimeType = data.get('mimeType','')
        # filename

        logger.error(args)
        logger.error(kwargs)
        
        pprint.PrettyPrinter(4).pprint(request)
        pprint.PrettyPrinter(4).pprint(args)
        pprint.PrettyPrinter(4).pprint(kwargs)

        # ALIOSS_ACCESS_KEY_ID = os.envi
        # ALIOSS_SECRET_ACCESS_KEY = os.
        # ALIOSS_SOURCE_BUCKET_NAME = os
        # ALIOSS_DESTINATION_BUCKET_NAME

        # auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        # # Endpoint以杭州为例，其它Region请按实际情况填写。
        # bucket = oss2.Bucket(auth,settings.ALIOSS_DESTINATION_ENDPOINT , settings.ALIOSS_DESTINATION_BUCKET_NAME)

        # # 设置此签名URL在60秒内有效。
        # bucket.sign_url('GET', , settings.ALIOSS_EXPIRES)

        return JsonResponse({'String value': 'OK', 'Key': 'Status','bucket':request.headers['X-Oss-Bucket'],'filename':filename,'mimeType':mimeType}, safe=False)

class AliMtsCallBack(APIView):
    def post(self,request,*args,**kwargs):
        '''
        用post方法
        '''
        import oss2
        import logging    
        logger = logging.getLogger('dev.error')
        logger.error('-------------------in post ----------------------')

        auth = request.META.get('Authorization')
        logger.error(auth)
        # if not request:
        #     return None
        logger.error(request)
        logger.error(request.headers)
        # X-Oss-Bucket
        # logger.error(request.POST)
        logger.error(request.body)
        logger.error(json.loads(request.body))
        # data = request.data
        # filename = data.get('filename', '')
        # mimeType = data.get('mimeType','')
        return JsonResponse({'String value': 'OK', 'Key': 'Status'}, safe=False)


