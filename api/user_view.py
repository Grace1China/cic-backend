from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated,AllowAny
from users.models import CustomUser
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import CustomUser4APISerializer,CustomUser4Info
from churchs.models import Sermon, WeeklyReport
from churchs.serializers import SermonSerializer, EweeklySerializer
import boto3
from botocore.exceptions import ClientError
import logging
from rest_framework import generics
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from django.contrib.auth.models import User,AnonymousUser
# from .serializers import userProfileSerializer
from churchs.models import Church
import pprint
from django.db.models import Q
from django.db import transaction
from rest_framework.decorators import action
import datetime
from datetime import timedelta
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
import traceback, sys 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
import logging
from .utill import CICUtill
from rest_framework_simplejwt.tokens import RefreshToken

theLogger = logging.getLogger('church.all')

class CustomUserViewSet(viewsets.ModelViewSet):
    '''
    定制用户类
    '''
    queryset=CustomUser.objects.all()
    serializer_class=CustomUser4APISerializer
    permission_classes=[AllowAny]
    @action(detail=True,methods=['POST'], format="json")
    def register(self,request):
        '''
        1 注册用户
        2 同时加入教会。要做一个二维码，有app的用户扫码出现注册页。码就自动填入教会
        '''
        try:
            data = self.request.data

            email = data.get("email",None)
            pwd = data.get('password', None)
            confirmpwd = data.get('confirmpwd', None)
            church_code = data.get('church_code', '-1')
            
            if email is None or email == "" or pwd is None or pwd == "" or confirmpwd is None or confirmpwd == "":
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)
            if pwd != confirmpwd:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "两次输入新密码不同", 'sysErrMsg': ''}, safe=False)
            
            existUser = self.get_queryset().filter(email=email).first()
            if existUser is not None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "该邮箱已被使用", 'sysErrMsg': ''}, safe=False)

            theChurch = Church.objects.get(Q(code=church_code))
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(church=theChurch,is_active=True)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            return JsonResponse({'errCode': '1001','msg': str(e), 'data': None}, safe=False)

    @action(detail=True, methods=['POST'], format="json")
    def login(self,request):
        
        data = request.data
        email = data.get("email", None)
        password = data.get('password', None)

        if email is None or email == "" or password is None or password == "":
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)

        existUser = self.get_queryset().filter(email=email).first()
        if existUser is None:
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "账号未注册", 'sysErrMsg': ''}, safe=False)
        
        if not existUser.check_password(password):
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "密码错误", 'sysErrMsg': ''}, safe=False)
        
        # import httplib2
        # import json
        
        # connect = httplib2.Http()
        # resp, content = connect.request("http://t:8000/rapi/auth/jwt/create",
        #                                 "POST",
        #                                 body=json.dumps({'email': email,'password':password}),
        #                                 headers={"Content-type": "application/json"})
        # connect.close()
        # if content is None:
        #     return JsonResponse({'errCode': '1001', 'data': None, 'msg': "创建token错误"}, safe=False)

        # 
        # decodedJson = json.loads(content)
        # jsonString = json.dumps(decodedJson)

        # 具体错误原因。
        # detail = decodedJson.get('detail')
        # if detail is not None:
        # return JsonResponse({'errCode': '1001', 'data': None, 'msg': detail}, safe=False)

        # refresh = decodedJson.get('refresh')
        # access = decodedJson.get('access')

        # # refresh = RefreshToken.for_user(user)
        
        from rest_framework_simplejwt import views
        vCreate =  views.TokenObtainPairView.as_view()
        resp = vCreate(request._request) 
        resp.render()
        theLogger.info('-----login---------')
        theLogger.info(resp)
        theLogger.info(resp.content)


        if resp.status_code != 200:
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "创建token错误"}, safe=False)
        
        return JsonResponse({'errCode': '0', 
                             'data':eval(resp.content), 
                             'msg': "success"}, safe=False)

    
    @transaction.atomic
    def perform_create(self, serializer):
        '''
        这个方法，可能有来自，djoser创建系统用户时，signal通知生成的。
        2 有可能又是前端发过来注册信息
        '''
        try:
            data = self.request.data
            church_code = data.get('church_code', '-1')
            pp.pprint(church_code)

            theChurch = Church.objects.get(Q(code=church_code))
            
            serializer.save(church=theChurch)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            return JsonResponse({'errCode': '1001','msg': str(e), 'data': serializer.data}, safe=False)

    # @action(detail=True,methods=['GET'], format="json")
    # def getInfo(self,request,email=''):
    #     ret = {'errCode': '1001'}
    #     try:
    #         user1 = CustomUser.objects.all().get(email__exact=email)
    #         if user1 is None:
    #             raise Exception('User not find')
    #         szUser = CustomUser4Info(instance=user1)
    #         ret = {'errCode': '0','msg':'success', 'data': szUser.data}
    #     except Exception as e:
    #         import traceback
    #         import sys
    #         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #         ret = {'errCode': '1001','msg':'there is an exception', 'data': None}
    #     finally:
    #         return JsonResponse(ret, safe=False)


class CustomUserInfoViewSet(viewsets.ModelViewSet):
    '''
    用户信息正式类
    '''
    queryset = CustomUser.objects.all()
    serializer_class = CustomUser4APISerializer
    permission_classes=[IsAuthenticated] #401,{ "detail": "身份认证信息未提供。"}

    '''
    获取用户信息
    '''
    @action(detail=True, methods=['GET'], format="json")
    def getUserInfo(self, request):
        ret = {'errCode': '1001', 'msg': '', 'data': None}
        try:
            user = request.user
            if user is None:
                return JsonResponse({'errCode': '1001', 'msg': 'User not find', 'data': None}, safe=False)
            if user is AnonymousUser:
                return JsonResponse({'errCode': '1001', 'msg': 'User not find', 'data': None}, safe=False)
            # if user is CustomUser: #判断不出来。
            szUser = CustomUser4Info(instance=user)
            ret = {'errCode': '0', 'msg': 'success', 'data': szUser.data}
        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            ret = {'errCode': '1001', 'msg': 'there is an exception', 'data': None}
        finally:
            return JsonResponse(ret, safe=False)
        
    '''
    修改用户信息
    '''
    @action(detail=True,methods=['POST'], format="json")
    def updateUserInfo(self,request):

        try:
            user = request.user
            if user is None or user is AnonymousUser:
                return JsonResponse({'errCode': '1001', 'msg': 'User not find', 'data': None}, safe=False)
            
            username = request.data.get('username', None)
            if username is None or username == "":
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)
            
            user.username = username
            user.save()

            szUser = CustomUser4Info(instance=user)
            
            return JsonResponse({'errCode': '0', 'data': szUser.data, 'msg': "success", 'sysErrMsg': ''}, safe=False)
        except Exception as e:
            return JsonResponse({'errCode': '1001','msg': str(e), 'data': None}, safe=False)

    '''
    修改密码
    '''
    @action(detail=True, methods=['POST'], format="json")
    def updateUserPWD(self, request):
        try:
            user = request.user
            if user is None or user is AnonymousUser:
                return JsonResponse({'errCode': '1001', 'msg': 'User not find', 'data': None}, safe=False)
    
            oldpwd = request.data.get('oldpwd', None)
            newpwd = request.data.get('newpwd', None)
            confirmpwd = request.data.get('confirmpwd', None)
            if oldpwd is None or oldpwd == "" or newpwd is None or newpwd == "" or confirmpwd is None or confirmpwd == "":
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)
    
            if not user.check_password(oldpwd):
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "老密码输入错误", 'sysErrMsg': ''}, safe=False)
            if newpwd != confirmpwd:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "两次输入新密码不同", 'sysErrMsg': ''}, safe=False)
            
            user.set_password(newpwd)
            user.save()
    
            return JsonResponse({'errCode': '0', 'data': None, 'msg': "success", 'sysErrMsg': ''}, safe=False)
        except Exception as e:
            return JsonResponse({'errCode': '1001', 'msg': str(e), 'data': None}, safe=False)











            

            

