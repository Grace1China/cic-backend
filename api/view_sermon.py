from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated,AllowAny
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
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
import traceback, sys 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
import traceback
from api.serializers import SermonListSerializer4API,SermonSerializer4API
from .views import *


theLogger = logging.getLogger('church.all')



from .utill import timeSpan
from datetime import datetime as dd

class SermonListViewSet(viewsets.ModelViewSet):
    '''
    主日信息列表。
    '''
    from django.db.models import Prefetch
    from churchs.models import Media
    queryset = Sermon.objects.prefetch_related(Prefetch('medias',queryset=Media.objects.order_by('kind')))
    # queryset=Sermon.objects.all()
    serializer_class = SermonListSerializer4API

    permission_classes = [AllowAny]
    @action(detail=True,methods=['get'], format="json")
    def GetLordsDayInfoList(self,request,page=1,pagesize=30):
        try:
            theLogger.info('start GetLordsDayInfoList-------------')
            tmspan = timeSpan(dd.now())
            

            page = getPage(request)
            pagesize = getPageSize(request)
            offset = int((page - 1) * pagesize)
            
            from django.conf import settings
            theCh = Church.objects.get(code=settings.DEFAULT_CHURCH_CODE)
            if not request.user.is_authenticated:
                if theCh == None:
                    return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有平台教会信息', 'sysErrMsg': ''},
                                        safe=False)
            else:
                theCh = request.user.church
                if theCh == None:
                    return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有教会信息', 'sysErrMsg': ''}, safe=False)

            theLogger.info(settings.DEFAULT_CHURCH_CODE)
            # now = datetime.datetime.now()
            # last_sunday = now - timedelta(days=now.weekday() + 1)
            # last_sunday = last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
            # this_saturday = now + timedelta(days=6 - now.weekday())
            # this_saturday = this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(
            #     microsecond=999)

            count = self.get_queryset().filter(church=theCh,
                                               status=Sermon.STATUS_PUBLISHED).order_by('-pub_time').count()
            theSermons = self.get_queryset().filter(church=theCh,
                                                   status=Sermon.STATUS_PUBLISHED).order_by('-pub_time')[offset:offset + pagesize]
            
            totalPage = getTotalPage(pagesize,count)
            
            # for sermon in theSermons:
            #     if sermon.pub_time >= last_sunday and sermon.pub_time <= this_saturday:
            #         sermon.isLastWeek = True
                
            slzSermons = self.get_serializer(theSermons, many=True)
            theLogger.info('end1 GetLordsDayInfoList---------tmspan.getSpan:%d----' % tmspan.getSpan(end=dd.now()))
            slzdt = slzSermons.data
            
            theLogger.info('end2 GetLordsDayInfoList---------tmspan.getSpan:%d----' % tmspan.getSpan(end=dd.now()))

            return JsonResponse({'errCode': '0', 'data': slzdt, 
                                 'page': page,
                                 'totalPage': totalPage}, safe=False)
        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse(
                {'errCode': '1001', 'data': None, 'msg': '教会没有最新讲道', 'sysErrMsg': traceback.format_exc()}, safe=False)


class SermonViewOneSet(viewsets.ModelViewSet):
    '''
    获取一个主日

    '''
    from .serializers import SermonSerializer4API, MediaSerializer4API
    from churchs.models import Media
    from django.db.models import Prefetch
    queryset = Sermon.objects.prefetch_related(Prefetch('medias',queryset=Media.objects.order_by('kind')))
    serializer_class = SermonSerializer4API
    permission_classes = [AllowAny]
    @action(detail=True, methods=['GET'], format="json")
    def GetLordsDayInfoByID(self, request,pk):
        '''
        根据id获取主日信息
        '''
        try:
            # if not request.user.is_authenticated:
            #     return JsonResponse({'errCode': '403', 'data': None, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''},
            #                         safe=False)
            
            # data = request.GET
            # sermonid = int(data.get('sermonid', -1))
            # if sermonid == -1:
            #     return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ""}, safe=False)
            theSermon = self.get_queryset().get(id=pk)
            if theSermon is None or theSermon.status!=Sermon.STATUS_PUBLISHED:
                raise Exception('no sermon for this id %d or sermon status is not published:%d' % (pk,Sermon.STATUS_PUBLISHED if Sermon else -1))
            # if theSermon is None:
            #     return JsonResponse({'errCode': '1001', 'data': None, 'msg': "没有主日信息", 'sysErrMsg': ""}, safe=False)
            slzSermon = self.get_serializer(theSermon)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse(
                {'errCode': '1001', 'data': None, 'msg': e.__str__(), 'sysErrMsg': traceback.format_exc()}, safe=False)

    @action(detail=True, methods=['POST'], format="json")  # , permission_classes=[AllowAny]
    def GetDefaultLordsDayInfo(self, request):
        '''
        查找默认教会主日信息
        '''
        try:
            from django.conf import settings
            theCh = Church.objects.get(code=settings.DEFAULT_CHURCH_CODE)
            if theCh == None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有平台教会信息', 'sysErrMsg': ''}, safe=False)
            now = datetime.datetime.now()
            last_sunday = now - timedelta(days=now.weekday() + 1)
            last_sunday = last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)

            this_saturday = now + timedelta(days=6 - now.weekday())
            this_saturday = this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(
                microsecond=999)

            theSermon = self.get_queryset().filter(church=theCh, pub_time__gte=last_sunday, pub_time__lte=this_saturday,
                                                   status=Sermon.STATUS_PUBLISHED).order_by('-pub_time').first()
            if theSermon is None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "没有主日信息", 'sysErrMsg': ""}, safe=False)
            slzSermon = self.get_serializer(theSermon)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:

            import traceback
            import sys
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse(
                {'errCode': '1001', 'data': None, 'msg': e.__str__(), 'sysErrMsg': traceback.format_exc()}, safe=False)

    @action(detail=True,methods=['get'], format="json")
    def GetNewestSermonMedias(self, request):
        '''
        查找最新主日的媒体例表。
        2 a.时间在周日，未来一天有主日信息，提示什么时间将播放。标题可以改成，主日信息
          b.时间在周日，这一天没有主日信息，提示没有最新内容
        3 时间不在主日，显示一个最近的主日信息。标题只可以改成最新内容
        '''
        try:
            from django.conf import settings
            theCh = request.user.church
            if theCh == None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有教会信息', 'sysErrMsg': ''}, safe=False)
            # from tzlocal import get_localzone
            # import time
            # from datetime import datetime
            import pytz
            tz = pytz.timezone('Asia/Shanghai') #东八区
            import datetime
            loc_dt = tz.localize(datetime.datetime.now())

            loc_dt_0 = loc_dt.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
            loc_dt_24 = loc_dt.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)

            if loc_dt.weekday() == 6 :
                # pass
                theSermon = self.get_queryset().filter(church=theCh, pub_time__gte=loc_dt_0, pub_time__lte=loc_dt_24,
                                                   status=Sermon.STATUS_PUBLISHED).order_by('pub_time').first()
                                                   #用升序，是因为主日如果有多堂，那么就是一堂一堂的显示，主日当天时间小的，先显示
            else:
                theSermon = self.get_queryset().filter(church=theCh, status=Sermon.STATUS_PUBLISHED).order_by('-pub_time').first()
                 #用降序，取最新的时间的主日

            if theSermon is None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "没有主日信息", 'sysErrMsg': ""}, safe=False)
            slzSermon = self.get_serializer(theSermon)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:
            import traceback
            # import sys
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse(
                {'errCode': '1001', 'data': None, 'msg': e.__str__(), 'sysErrMsg': traceback.format_exc()}, safe=False)    
















# class SermonViewSet(viewsets.ModelViewSet):
#     '''
#     讲道视图，功能：1 按教会取主日讲道; 2 取平台讲道
#     
#     '''
#     from .serializers import SermonSerializer4API, MediaSerializer4API
#     from churchs.models import Media
#     from django.db.models import Prefetch
#     queryset = Sermon.objects.prefetch_related(Prefetch('medias',
#         queryset=Media.objects.order_by('kind')))
#     serializer_class=SermonSerializer4API
#     # permission_classes = [AllowAny]
#     @action(detail=True,methods=['POST'], format="json",permission_classes=[IsAuthenticated])
#     def GetCurrentLordsDayInfo(self,request):
#         '''
#         查找当前用户所在教会主日信息
#         '''
#         try:
#             if not request.user.is_authenticated :
#                 return JsonResponse({'errCode': '403', 'data': None,'msg':'您没有执行该操作的权限。','sysErrMsg':''}, safe=False)
#         
#             if request.user.church == None:
#                 return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有教会信息','sysErrMsg':''}, safe=False)
#             now = datetime.datetime.now()
#             last_sunday = now - timedelta(days=now.weekday()+1)
#             last_sunday=last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
# 
#             this_saturday = now + timedelta(days=6-now.weekday())
#             this_saturday=this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)
# 
#             theSermon = self.get_queryset().filter(church=request.user.church,pub_time__gte=last_sunday,pub_time__lte=this_saturday,status=Sermon.STATUS_PUBLISHED).order_by('-pub_time').first()
#             if theSermon is None:
#                 return JsonResponse({'errCode': '1001', 'data': None, 'msg': "没有主日信息", 'sysErrMsg': ""},safe=False)
#             slzSermon = self.get_serializer(theSermon)
#             # from churchs.models import Media
#             # from .serializers import MediaSerializer4API
# 
#             # slzSermon.data['medias'] =  MediaSerializer4API(Media.objects.all().filter(owner=theSermon))
#             # print(Media.objects.all().filter(owner=theSermon))
#             # print(slzSermon.medias)
#             return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
#         except Exception as e:
#             import traceback
#             import sys
#             theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
#             return JsonResponse({'errCode': '1001', 'data': None,'msg':e.__str__(),'sysErrMsg':traceback.format_exc()}, safe=False)
# 
#     @action(detail=True,methods=['POST'], format="json")#, permission_classes=[AllowAny]
#     def GetDefaultLordsDayInfo(self,request):
#         '''
#         查找默认教会主日信息
#         '''
#         try:
#             from django.conf import settings
#             theCh = Church.objects.all().get(code=settings.DEFAULT_CHURCH_CODE)
#             if theCh == None:
#                 return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有平台教会信息','sysErrMsg':''}, safe=False)
#             now = datetime.datetime.now()
#             last_sunday = now - timedelta(days=now.weekday()+1)
#             last_sunday=last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
# 
#             this_saturday = now + timedelta(days=6-now.weekday())
#             this_saturday=this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)
# 
#             theSermon = self.get_queryset().filter(church=theCh,pub_time__gte=last_sunday,pub_time__lte=this_saturday,status=Sermon.STATUS_PUBLISHED).order_by('-pub_time').first()
#             if theSermon is None:
#                 return JsonResponse({'errCode': '1001', 'data': None, 'msg': "没有主日信息", 'sysErrMsg': ""},safe=False)
#             slzSermon = self.get_serializer(theSermon)
#             return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
#         except Exception as e:
# 
#             import traceback
#             import sys
#             theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
#             return JsonResponse({'errCode': '1001', 'data': None,'msg':e.__str__(),'sysErrMsg':traceback.format_exc()}, safe=False)
#     
#     def get_permissions(self):
#         """
#         Instantiates and returns the list of permissions that this view requires.
#         """
#         theLogger.info(self)
# 
#         theLogger.info(self.action)
#         if self.action == 'GetDefaultLordsDayInfo':
#             permission_classes = [AllowAny]
#         else:
#             permission_classes = [IsAuthenticated]
#         return [permission() for permission in permission_classes]


