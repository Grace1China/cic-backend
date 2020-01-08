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
import datetime
from datetime import timedelta

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


# class EweeklyView(APIView):
#     '''
#     取eweekly 
#     '''
#     def get_object(self, pk):
#         try:
#             return WeeklyReport.objects.get(pk=pk)
#         except WeeklyReport.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         '''
#         retrieve sermon data
#         '''
#         eweekly = None
#         print('----------------->'+str(pk))
#         if pk == None or int(pk) <= 0:
#             #选一个最近的sermon
#             eweeklyQry = WeeklyReport.objects.all()
#             eweekly = eweeklyQry.reverse()[:1]
#             if len(eweekly) != 1:
#                 return JsonResponse({'errCode': '1001', msg:'database has no record.','data':None}, safe=False)
#             else:
#                 eweekly = eweekly[0]

#             print('---------pk <=0------------')
#             print(eweekly)
#             serializer = EweeklySerializer(eweekly)
#         else: 
#             eweekly = self.get_object(pk)
#             print('---------pk >0------------')
#             serializer = EweeklySerializer(eweekly)
            
#         return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)


class EweeklyViewSet(viewsets.ModelViewSet):
    '''
    查找平台周报和教会周报
    '''
    from churchs.models import WeeklyReport
    queryset=WeeklyReport.objects.all()
    serializer_class=EweeklySerializer
    permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['POST'], format="json")
    def GetChurchEweekly(self,request,pk):
        '''
        查找用户所属教会的最新周报 or 根据pk查找
        '''
        try:
            if pk == None or int(pk) <= 0:
                pprint.PrettyPrinter(indent=4).pprint(request.user)

                wr = self.get_queryset().filter(church=request.user.church, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')[0]
            else: 
                wr = self.get_object(pk)

            serializer = self.get_serializer(wr)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            return JsonResponse({'errCode': '1001', 'msg':'教会没有最新的周报','data': {},'sysErrMsg':e.__str__()}, safe=False)

    @action(detail=True,methods=['POST'], format="json")
    def GetL3Eweekly(self,request):
        '''
        查找L3平台最新周报
        '''
        # data = self.request.data
        ch = Church.objects.filter(Q(code__iexact='l3'))[0]
        pprint.PrettyPrinter(indent=4).pprint(ch)
        
        try:
            wr = self.get_queryset().filter(church=ch, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')
            # pprint.PrettyPrinter(indent=4).pprint(wr)
            wr = wr[0]
            serializer = self.get_serializer(wr)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            # pprint.PrettyPrinter(indent=4).pprint(IndexError)
            return JsonResponse({'errCode': '1001', 'msg':'L3没有最新的周报','data': {},'sysErrMsg':e.__str__()}, safe=False)
            



class ChurchViewSet(viewsets.ModelViewSet):
    '''
    取教会信息，根据用户所属的教会，查找教会。
    '''
    from .serializers import ChurchSerializer4API
    queryset=Church.objects.all()
    serializer_class=ChurchSerializer4API
    permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['POST'], format="json")
    def GetUserChurch(self,request):
        '''
        查找用户所属教会
        '''
        serializer = self.get_serializer(request.user.church)
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)


class SermonViewSet(viewsets.ModelViewSet):
    '''
    讲道视图，功能：1 按教会取主日讲道; 2 取平台讲道
    
    '''
    from .serializers import SermonSerializer4API, MediaSerializer4API
    from churchs.models import Media
    from django.db.models import Prefetch
    # queryset=Sermon.objects.all()
    queryset = Sermon.objects.prefetch_related(Prefetch('medias',
        queryset=Media.objects.order_by('kind')))
    serializer_class=SermonSerializer4API
    permission_classes=[IsAuthenticated]

    @action(detail=True,methods=['POST'], format="json")
    def GetCurrentLordsDayInfo(self,request):
        '''
        查找当前用户所在教会主日信息
        '''
        try:
            if (request.user.church == None):
                return JsonResponse({'errCode': '1001', 'data': {},'msg':'没有教会信息','sysErrMsg':''}, safe=False)
            now = datetime.datetime.now()
            last_sunday = now - timedelta(days=now.weekday()+1)
            last_sunday=last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)

            this_saturday = now + timedelta(days=6-now.weekday())
            this_saturday=this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)

            theSermon = self.get_queryset().filter(church=request.user.church,pub_time__gte=last_sunday,pub_time__lte=this_saturday,status=Sermon.STATUS_PUBLISHED).order_by('-pub_time')[0]
            slzSermon = self.get_serializer(theSermon)
            # from churchs.models import Media
            # from .serializers import MediaSerializer4API

            # slzSermon.data['medias'] =  MediaSerializer4API(Media.objects.all().filter(owner=theSermon))
            # print(Media.objects.all().filter(owner=theSermon))
            # print(slzSermon.medias)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:
            # pprint.PrettyPrinter(4).pprint(e.__traceback__)
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'data': {},'msg':'教会没有最新讲道','sysErrMsg':e.__str__()}, safe=False)

    @action(detail=True,methods=['POST'], format="json")
    def GetDefaultLordsDayInfo(self,request):
        '''
        查找当前用户所在教会主日信息
        '''
        try:
            from django.conf import settings
            theCh = Church.objects.all().get(code = settings.DEFAULT_CHURCH_CODE)
            if (theCh == None):
                return JsonResponse({'errCode': '1001', 'data': {},'msg':'没有平台教会信息','sysErrMsg':''}, safe=False)
            now = datetime.datetime.now()
            last_sunday = now - timedelta(days=now.weekday()+1)
            last_sunday=last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)

            this_saturday = now + timedelta(days=6-now.weekday())
            this_saturday=this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)

            theSermon = self.get_queryset().filter(church=request.user.church,pub_time__gte=last_sunday,pub_time__lte=this_saturday,status=Sermon.STATUS_PUBLISHED).order_by('-pub_time')[0]
            slzSermon = self.get_serializer(theSermon)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:
            return JsonResponse({'errCode': '1001', 'data': {},'msg':'平台教会没有最新讲道','sysErrMsg':e.__str__()}, safe=False)

    # @action(detail=True,methods=['POST'], format="json")
    # def GetChurchLordsDayInfo(self,request,pk):
    #     '''
    #     查找用户所属教会的主日信息.1 根据教会查找主日信息 2 在主日信息里面充实媒体信息
    #     选根据pk查找，如果pk小于等于0 查当前最新讲道；
    #     如果pk>0 查当前教会指定讲道
    #     如果pk不是数字报错 "主键必须是整数"
    #     '''
    #     try:
    #         if pk == None or int(pk) <= 0:
    #             return JsonResponse({'errCode': '1002', 'data': {},'msg':'讲道id不正确','sysErrMsg':e.__str__()}, safe=False)
    #             theSermon = self.get_queryset().filter(church=request.user.church).order_by('-pub_time')[0]
    #         else:
    #             theSermon = self.get_object(pk)
            
    #         #
    #         slzSermon = self.get_serializer(theSermon)
    #         return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)
    #     except Exception as e:
    #         return JsonResponse({'errCode': '1001', 'data': {},'msg':'教会没有最新讲道','sysErrMsg':e.__str__()}, safe=False)

    # @action(detail=True,methods=['POST'], format="json")
    # def GetDefaultLordsDayInfo(self,request,pk):
    #     '''
    #     查找平台默认讲道
    #     根据setting中的教会编码查找教会，如果不存在教会，报错默认教会不存在
    #     根据默认教会查找讲道，不存在报错，默认教会不存在讲道
        
    #     '''
    #     try:
    #         if pk == None or int(pk) <= 0:
    #             pprint.PrettyPrinter(indent=4).pprint(request.user)

    #             wr = self.get_queryset().filter(church=request.user.church, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')[0]
    #         else: 
    #             wr = self.get_object(pk)

    #         serializer = self.get_serializer(wr)
    #         return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

    #     except Exception as e:
    #         return JsonResponse({'errCode': '1001', 'msg':'教会没有最新的周报','data': {},'sysErrMsg':e.__str__()}, safe=False)

