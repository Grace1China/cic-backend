from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated
from .models import userProfile
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import userProfileSerializer
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


# Create your views here.
class UserProfileViewSet(viewsets.ModelViewSet):
    '''
    我现在是要加一个注册，返回一个用户信息，并且加入教会码。如何生成教会码呢？在教会对像的后台，加入一个码就可以了。
    请使用这个json做例子
    {  
    "church_code": "086-010-0010",
    "description": "aa3",
    "email": "aa1@bicf.org",
    "location": "aa3",
    "password": "aa1_123456",
    "role": "2",
    "username": "aa3"
    }
    这个码是一人一个码。（小组同）
    有了这个码，我就可以在这里反查教会了。现在过来的信息，有名称，邮箱，教会邀请码
    '''
    queryset=userProfile.objects.all()
    serializer_class=userProfileSerializer
    # permission_classes=[IsAuthenticated]


    @transaction.atomic
    def perform_create(self, serializer):
        '''
        这个方法，可能有来自，djoser创建系统用户时，signal通知生成的。
        2 有可能又是前端发过来注册信息
        '''
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.request.data)
        # self.request.POST
        # print(self.request)
        data = self.request.data
        church_code = data.get('church_code', '-1')
        pp.pprint(church_code)

        theChurch = Church.objects.get(Q(code=church_code))
        


        user=self.request.user
        if isinstance(self.request.user,AnonymousUser):
            user = User.objects.create_user(username=data.get('username', ''),email=data.get('email',''),password=data.get("password",''))

        pp.pprint(theChurch)
        pp.pprint(user)
        serializer.save(user=user,church=theChurch)
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)



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

    
