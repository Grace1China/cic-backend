from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import CustomUser4APISerializer
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



# Create your views here.
class CustomUserViewSet(viewsets.ModelViewSet):
    '''
    "email": "daniel_2@bicf.org",
    "username": "d2",
    "password": "2wsx3edc",
    "church_code": "086-010-0001" 同时加入教会。要做一个二维码，有app的用户扫码出现注册页。码就自动填入
    '''
    queryset=CustomUser.objects.all()
    serializer_class=CustomUser4APISerializer
    # permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['POST'], format="json")
    def register(self,request):
        '''
        1 注册用户
        2 同时加入教会。要做一个二维码，有app的用户扫码出现注册页。码就自动填入教会
        '''
        try:
            data = self.request.data
            church_code = data.get('church_code', '-1')
            # pp.pprint(church_code)

            theChurch = Church.objects.get(Q(code=church_code))
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(church=theChurch,is_active=True)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            return JsonResponse({'errCode': '1001','msg': str(e), 'data':{}}, safe=False)

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
            
        
        
    


# class userProfileDetailView(APIView):
#     queryset=userProfile.objects.all()
#     serializer_class=userProfileSerializer
#     permission_classes=[IsOwnerProfileOrReadOnly,IsAuthenticated]


class SermonDetailView(APIView):
    '''
    retrieve and update sermon
    # 1、首先要实现一个能查找主日信息的api可以返回主日的所有信息，现在只要实现当前主日信息 这个信息里面有id title cover pdf worship sermon giving等信息
    # 2、在这个信息中，应该可以自定义presignedurl的过期时间。这些都已经是presignedurl了。
    '''
    def get_object(self, pk):
        try:
            return Sermon.objects.get(pk=pk)
        except Sermon.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        '''
        retrieve sermon data
        '''
        sermon = None
        print('----------------->'+str(pk))
        if pk == None or int(pk) <= 0:
            #选一个最近的sermon
            sermonQry = Sermon.objects.all()
            sermon = sermonQry.reverse()[:1]
            if len(sermon) != 1:
                return JsonResponse({'errCode': '1001', msg:'database has no record.','data':None}, safe=False)
            else:
                sermon = sermon[0]

            print('---------pk <=0------------')
            print(sermon)
            serializer = SermonSerializer(sermon)
        else: 
            sermon = self.get_object(pk)
            print('---------pk >0------------')
            serializer = SermonSerializer(sermon)
            
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)


class EweeklyView(APIView):
    '''
    取eweekly 
    '''
    def get_object(self, pk):
        try:
            return WeeklyReport.objects.get(pk=pk)
        except WeeklyReport.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        '''
        retrieve sermon data
        '''
        eweekly = None
        print('----------------->'+str(pk))
        if pk == None or int(pk) <= 0:
            #选一个最近的sermon
            eweeklyQry = WeeklyReport.objects.all()
            eweekly = eweeklyQry.reverse()[:1]
            if len(eweekly) != 1:
                return JsonResponse({'errCode': '1001', msg:'database has no record.','data':None}, safe=False)
            else:
                eweekly = eweekly[0]

            print('---------pk <=0------------')
            print(eweekly)
            serializer = EweeklySerializer(eweekly)
        else: 
            eweekly = self.get_object(pk)
            print('---------pk >0------------')
            serializer = EweeklySerializer(eweekly)
            
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

class ChurchViewSet(viewsets.ModelViewSet):
    '''
    取教会信息，根据用户所属的教会，查找教会。
    '''
    from .serializers import ChurchSerializer4API
    queryset=Church.objects.all()
    serializer_class=ChurchSerializer4API
    # permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['POST'], format="json")
    def GetUserChurch(self,request):
        '''
        查找用户所属教会
        '''
        serializer = self.get_serializer(request.user.church)
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)


