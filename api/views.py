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

def getPermissionClass():
    if settings.RUNTIME == 'sandbox':
        return AllowAny()
    else:
        return IsAuthenticated()

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
    permission_classes=[getPermissionClass]
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
            return JsonResponse({'errCode': '1001','msg': str(e), 'data': None}, safe=False)

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
            


class EweeklyViewSet(viewsets.ModelViewSet):
    '''
    查找平台周报和教会周报
    '''
    from churchs.models import WeeklyReport
    queryset=WeeklyReport.objects.all()
    serializer_class=EweeklySerializer
    permission_classes=[getPermissionClass]
    @action(detail=True,methods=['POST'], format="json")
    def GetChurchEweekly_v2(self,request):
        '''
        查找用户所属教会的最新周报 or 根据pk查找
        '''
        if not request.user.is_authenticated :
                return JsonResponse({'errCode': '403', 'data': None,'msg':'您没有执行该操作的权限。','sysErrMsg':''}, safe=False)
        try:
            wr = self.get_queryset().filter(church=request.user.church, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')[0]
            serializer = self.get_serializer(wr)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'msg':'教会没有最新的周报','data': None,'sysErrMsg':traceback.format_exc()()}, safe=False)



    @action(detail=True,methods=['POST'], format="json")
    def del_GetChurchEweekly(self,request,pk):
        '''
        查找用户所属教会的最新周报 or 根据pk查找
        '''
        if not request.user.is_authenticated :
                return JsonResponse({'errCode': '403', 'data': None,'msg':'您没有执行该操作的权限。','sysErrMsg':''}, safe=False)
        try:
            wr = self.get_queryset().filter(church=request.user.church, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')[0]
            serializer = self.get_serializer(wr)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'msg':'教会没有最新的周报','data': None,'sysErrMsg':traceback.format_exc()()}, safe=False)


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
            traceback.print_exc(file=sys.stdout)
            # pprint.PrettyPrinter(indent=4).pprint(IndexError)
            return JsonResponse({'errCode': '1001', 'msg':'L3没有最新的周报','data': None,'sysErrMsg':traceback.format_exc()()}, safe=False)

            



class ChurchViewSet(viewsets.ModelViewSet):
    '''
    取教会信息，根据用户所属的教会，查找教会。
    '''
    from .serializers import ChurchSerializer4API
    queryset=Church.objects.all()
    serializer_class=ChurchSerializer4API
    permission_classes=[getPermissionClass]
    @action(detail=True,methods=['POST'], format="json")
    def GetUserChurch(self,request):
        '''
        查找用户所属教会
        '''
        import logging 
        loger = logging.getLogger('church.all')
        loger.info(request.user)
        if isinstance (request.user,AnonymousUser):
            ch = Church.objects.all().fillter(code=settings.DEFAULT_CHURCH)
            serializer = self.get_serializer(ch)
        else:
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
    permission_classes=[getPermissionClass]


    @action(detail=True,methods=['POST'], format="json",permission_classes=[IsAuthenticated])
    def GetCurrentLordsDayInfo(self,request):
        '''
        查找当前用户所在教会主日信息
        '''
        if not request.user.is_authenticated :
                return JsonResponse({'errCode': '403', 'data': None,'msg':'您没有执行该操作的权限。','sysErrMsg':''}, safe=False)
        try:
            if (request.user.church == None):
                return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有教会信息','sysErrMsg':''}, safe=False)
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
            return JsonResponse({'errCode': '1001', 'data': None,'msg':'教会没有最新讲道','sysErrMsg':traceback.format_exc()}, safe=False)

    @action(detail=True,methods=['POST'], format="json")
    def GetDefaultLordsDayInfo(self,request):
        '''
        查找当前用户所在教会主日信息
        '''
        try:
            from django.conf import settings
            theCh = Church.objects.all().get(code = settings.DEFAULT_CHURCH_CODE)
            if (theCh == None):
                return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有平台教会信息','sysErrMsg':''}, safe=False)
            now = datetime.datetime.now()
            last_sunday = now - timedelta(days=now.weekday()+1)
            last_sunday=last_sunday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)

            this_saturday = now + timedelta(days=6-now.weekday())
            this_saturday=this_saturday.replace(hour=23).replace(minute=59).replace(second=59).replace(microsecond=999)

            theSermon = self.get_queryset().filter(church=theCh,pub_time__gte=last_sunday,pub_time__lte=this_saturday,status=Sermon.STATUS_PUBLISHED).order_by('-pub_time')[0]
            slzSermon = self.get_serializer(theSermon)
            return JsonResponse({'errCode': '0', 'data': slzSermon.data}, safe=False)
        except Exception as e:

            import traceback
            import sys
            loger = logging.getLogger('church.all')
            loger.exception('there is exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'data': None,'msg':'平台教会没有最新讲道','sysErrMsg':traceback.format_exc()}, safe=False)



from .serializers import CourseSerializer4API, MediaSerializer4API, CourseSerializer4APIPOST
class  CourseViewSet(viewsets.ModelViewSet):
    '''
    课程视图
    
    '''
    from churchs.models import Media
    from church.models import Course
    from django.db.models import Prefetch
    
    # from .schema_view import  CustomSchema
    queryset = Course.objects.prefetch_related(Prefetch('medias',
        queryset=Media.objects.order_by('kind')))
    serializer_class=CourseSerializer4APIPOST
    permission_classes=[getPermissionClass]

    # schema = CustomSchema()
    # from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

    @action(detail=True,methods=['get','post'], format="json")
    def GetCourseList(self,request,page=1,pagesize=10,keyword=None,orderby=None,bought=False):
        '''
        查找课程列表信息
        '''
        try:
            logger = logging.getLogger('dev.error')

            logger.error(request.META)
          

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                #pprint.PrettyPrinter(6).pprint(data)
                page = int(data.get('page', page))
                pagesize = int(data.get('pagesize', pagesize))
                keyword = data.get('keyword', keyword)
                orderby = data.get('orderby', orderby)
            else:
                
                # data = eval(request.body)
                # pprint.PrettyPrinter(4).pprint(data)
                logger.error(request.body)
                sbody = str(request.body,'utf-8')
                from ast import literal_eval
                data = literal_eval(sbody)
                page = int(data.get('page', page))
                pagesize = int(data.get('pagesize', pagesize))
                keyword = data.get('keyword', keyword)
                orderby = data.get('orderby', orderby)

            # data = self.request.data
            # church_code = data.get('church_code', '-1')

            if pagesize <=0 or pagesize >100 :
                return JsonResponse({'errCode': '1002', 'data': None,'msg':'pagesize要求是[1-100]','sysErrMsg':''}, safe=False)
            if page < 0 :
                return JsonResponse({'errCode': '1003', 'data': None,'msg':'page必有大于等于0','sysErrMsg':''}, safe=False)

            if orderby is not None:
                orderpair = orderby.split(' ') 
                orderby = '%s%s' % ('-' if((len(orderpair)==2) and (orderpair[1].lower() =='desc')) else '',orderpair[0])
            else:
                orderby = '-update_time'

            #查询已经购买新逻辑
            
            if data.get('bought', bought).lower() == 'true':
                queryBought = True
            else:
                queryBought = False
                
            if queryBought:
                from churchs.models import Media
                from church.models import Course
                from django.db.models import Prefetch
                if request.user.is_authenticated:
                    queryset = request.user.courses.all().prefetch_related(Prefetch('medias',
                                                             queryset=Media.objects.order_by('kind')))
                    courseList = queryset.order_by(orderby)
                    for course in courseList:
                        course.is_buy = True
                    page = 1
                    pagesize = 99999
                    paginator = Paginator(courseList, pagesize)
                    coursePage = paginator.get_page(page)
    
                    slzCourseList = CourseSerializer4API(coursePage, many=True)
                    # 前端需要用来取页面 
                    return JsonResponse({'errCode': '0', 'data': slzCourseList.data, 'page': coursePage.number,
                                         'totalPage': paginator.num_pages}, safe=False)
                else:
                    return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有课程列表'},
                                        safe=False)
            
            #未购买逻辑
            if keyword is not None:
                courseList = self.get_queryset().filter(Q(title__contains=keyword) | Q(content__contains=keyword) | Q(description__contains=keyword) | Q(church__name__contains=keyword) | Q(teacher__name__contains=keyword) | Q(medias__title__contains=keyword) | Q(medias__content__contains=keyword)).order_by(orderby)
            else:
                courseList = self.get_queryset().filter().order_by(orderby)
            
            addSalesInfosOnList(courseList, request.user)
            paginator = Paginator(courseList, pagesize)
            coursePage = paginator.get_page(page)

            slzCourseList = CourseSerializer4API(coursePage, many=True)
            # 前端需要用来取页面 
            return JsonResponse({'errCode': '0', 'data': slzCourseList.data, 'page':coursePage.number, 'totalPage':paginator.num_pages}, safe=False)
        except Exception as e:
            # pprint.PrettyPrinter(4).pprint(e.__traceback__)
            import traceback
            import sys
            logger = logging.getLogger('dev.error')
            traceback.print_exc(file=logger.handlers[0]._open())
            traceback.print_exc(file=sys.stdout)
            # logger.error()

            return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程列表','sysErrMsg':traceback.format_exc()()}, safe=False)


    @action(detail=True,methods=['POST'], format="json")
    def GetCoursebyID(self,request,pk):
        '''
        按照id查找课程信息
        '''
        try:
            course = self.get_queryset().filter(id=pk).order_by('-update_time')[0]

            addSalesInfosOn(course, request.user)
            slzCourse = CourseSerializer4API(course)
            return JsonResponse({'errCode': '0', 'data': slzCourse.data}, safe=False)
        except Exception as e:
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程列表','sysErrMsg':traceback.format_exc()()}, safe=False)

    
    @action(detail=True,methods=['post'], format="json")
    def SearchCourse(self,request):
        '''
        查找课程
        '''
        try:
            data = request.data
            keyword = data.get('keyword', '')
            if keyword == '':
                import traceback
                import sys
                traceback.print_exc(file=sys.stdout)
                return JsonResponse({'errCode': '1001', 'data': None,'msg':'搜索关键词不能为空','sysErrMsg':traceback.format_exc()()}, safe=False)


            courseList = self.get_queryset().filter(Q(title__contains=keyword) | Q(content__contains=keyword) | Q(description__contains=keyword) | Q(church__name__contains=keyword) | Q(teacher__name__contains=keyword) | Q(medias__title__contains=keyword) | Q(medias__content__contains=keyword)).order_by('-update_time')
            # paginator = Paginator(courseList, pagesize)
            # coursePage = paginator.get_page(page)
            
            addSalesInfosOnList(courseList,request.user)
            slzCourseList = CourseSerializer4API(courseList, many=True)
            # 前端需要用来取页面 
            return JsonResponse({'errCode': '0', 'data': slzCourseList.data}, safe=False)
        except Exception as e:
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程列表','sysErrMsg':traceback.format_exc()()}, safe=False)



def addSalesInfosOnList(courseList,user):
    for course in courseList:
        addSalesInfosOn(course,user)
   
def addSalesInfosOn(course,user):
    # course表自带sales_num，不再查询关联表了。用于orderby。
    # course.sales_num = course.users.all().count
    if course.users.all().filter(pk=user.id):
        course.is_buy = True
    else:
        course.is_buy = False
   
