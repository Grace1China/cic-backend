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
from .view_sermon import *


theLogger = logging.getLogger('church.all')


def getPermissionClass():
    from .utill import CICUtill
    return CICUtill.getPermissionClass()
    # if settings.RUNTIME == 'sandbox':
    #     return AllowAny()
    # else:
    #     return IsAuthenticated()

# Create your views here.

class EweeklyViewSet(viewsets.ModelViewSet):
    '''
    查找平台周报和教会周报
    '''
    from churchs.models import WeeklyReport
    queryset=WeeklyReport.objects.all()
    serializer_class=EweeklySerializer
    # permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['POST'], format="json")  #,permission_classes=[IsAuthenticated]这个地方不生效，官方文档有这个用法：）
    def GetChurchEweekly_v2(self,request):
        '''
        查找用户所属教会的最新周报 or 根据pk查找
        '''
        try:

            if not request.user.is_authenticated:
                return JsonResponse({'errCode': '403', 'data': None,'msg':'您没有执行该操作的权限。','sysErrMsg':''}, safe=False)
            wr = self.get_queryset().filter(church=request.user.church, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')[0]
            serializer = self.get_serializer(wr)
            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg':'教会没有最新的周报','data': None,'sysErrMsg':traceback.format_exc()}, safe=False)
        



    #可以无token直接访问。
    @action(detail=True,methods=['POST'], format="json")#,,permission_classes=[AllowAny]
    def GetL3Eweekly(self,request):
        '''
        查找L3平台最新周报
        '''
        ret = {'errCode': '0'}
        try:
            # data = self.request.data
            ch = Church.objects.filter(Q(code__iexact='l3'))[0]
            # pprint.PrettyPrinter(indent=4).pprint(ch)
            theLogger.info(ch)
            wr = self.get_queryset().filter(church=ch, status=WeeklyReport.STATUS_PUBLISHED).order_by('-pub_time')
            # pprint.PrettyPrinter(indent=4).pprint(wr)
            
            theLogger.info(wr)
            wr = wr[0]

            serializer = self.get_serializer(wr)
            ret = {'errCode': '0', 'data': serializer.data}
            return JsonResponse(ret, safe=False)
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            ret = {'errCode': '1001', 'msg':'L3没有最新的周报','data': None,'sysErrMsg':traceback.format_exc()}
        finally:
            # pprint.PrettyPrinter(indent=4).pprint(IndexError)
            return JsonResponse(ret, safe=False)


    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        theLogger.info(self)
        theLogger.info(self.action)
        if self.action == 'GetL3Eweekly':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

            



class ChurchViewSet(viewsets.ModelViewSet):
    '''
    取教会信息，根据用户所属的教会，查找教会。
    '''
    from .serializers import ChurchSerializer4API
    queryset=Church.objects.all()
    serializer_class=ChurchSerializer4API
    permission_classes = [AllowAny]
    @action(detail=True,methods=['POST'], format="json")
    def GetUserChurch(self,request):
        '''
        查找用户所属教会
        '''
        try:
            theLogger.info(request.user)
            if isinstance (request.user,AnonymousUser):
                ch = Church.objects.all().filter(code=settings.DEFAULT_CHURCH_CODE)
                if ch == None or len(ch)<=0:
                    raise Exception('default church was not find')
                else:
                    serializer = self.get_serializer(ch[0])
            else:
                serializer = self.get_serializer(request.user.church)

            return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)
        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            # pprint.PrettyPrinter(indent=4).pprint(IndexError)
            return JsonResponse({'errCode': '1001', 'msg':'没有找到用户的教会','data': None,'sysErrMsg':traceback.format_exc()}, safe=False)


    
def getPage(request):
    data = request.GET
    page = int(data.get('page', 1))
    if page < 0:
        page = 1
    return page

def getPageSize(request):
    data = request.GET
    pagesize = int(data.get('pagesize', 30))
    if pagesize < 0:
        pagesize = 0
    if pagesize > 100:
        pagesize = 100
    return pagesize

def getTotalPage(pagesize,count):
    if count == 0:
        return 0
    elif count <= pagesize:
        return 1
    elif count > pagesize:
        if count % pagesize > 0:
            return int(count / pagesize) + 1
        else:
            return int(count / pagesize)
        
    
from .serializers import CourseSerializer4API, MediaSerializer4API, CourseSerializer4APIPOST
class  CourseViewSet(viewsets.ModelViewSet):
    '''
    课程视图
    
    '''
    from churchs.models import Media
    from church.models import Course
    from django.db.models import Prefetch
    
    queryset = Course.objects.prefetch_related(Prefetch('medias',
        queryset=Media.objects.order_by('kind')))
    serializer_class=CourseSerializer4APIPOST
    permission_classes=[AllowAny]

    @action(detail=True,methods=['get','post'], format="json")
    def GetCourseList(self,request,page=1,pagesize=30,keyword=None,orderby=None,bought='false'):
        '''
        查找课程列表信息
        '''
        try:
            theLogger.info('start GetCourseList-------------')
            tmspan = timeSpan(dd.now())
            

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                theLogger.info(data)
                page = getPage(request)
                pagesize = getPageSize(request)
                offset = int((page - 1) * pagesize)
                keyword = data.get('keyword', keyword)
                orderby = data.get('orderby', orderby)
            else:         
                sbody = str(request.body,'utf-8')
                from ast import literal_eval
                data = literal_eval(sbody)
                page = int(data.get('page', page))
                pagesize = int(data.get('pagesize', pagesize))
                offset = int((page - 1) * pagesize)
                keyword = data.get('keyword', keyword)
                orderby = data.get('orderby', orderby)

            if orderby is not None:
                orderpair = orderby.split(' ') 
                orderby = '%s%s' % ('-' if((len(orderpair)==2) and (orderpair[1].lower() =='desc')) else '',orderpair[0])
            else:
                orderby = '-update_time'

            theLogger.info(data)
            #查询已经购买新逻辑
            if data.get('bought', bought).lower() == 'true':

                theLogger.info('data.get(bought, bought) = %s' % data.get('bought', bought))
                if not request.user.is_authenticated:
                    raise Exception('user need login to query bought list')
                    
                qr = self.get_queryset().filter(users=request.user)
                courseList = qr.order_by(orderby)[offset:offset + pagesize]
                for course in courseList:
                    course.is_buy = True

                slzCourseList = CourseSerializer4API(courseList, many=True)
                # 前端需要用来取页面 
                return JsonResponse({'errCode': '0', 'data': slzCourseList.data,
                                        'page': page,
                                        'totalPage': getTotalPage(pagesize,qr.count())}, safe=False)

         
            else:
                #未购买逻辑
                count = 0
                if keyword is not None:
                    queryset = self.get_queryset().filter(Q(title__contains=keyword) | Q(content__contains=keyword) | Q(description__contains=keyword) | Q(church__name__contains=keyword) | Q(teacher__name__contains=keyword) | Q(medias__title__contains=keyword) | Q(medias__content__contains=keyword))
                    count = queryset.count()
                    courseList = queryset.order_by(orderby)[offset:offset + pagesize]
                else:
                    queryset = self.get_queryset()
                    count = queryset.count()
                    courseList = queryset.order_by(orderby)[offset:offset + pagesize]
            for course in courseList:
                    course.is_buy = len(course.users.filter(id=request.user.id))>0
            
            # addSalesInfosOnList(courseList, request.user)

            slzCourseList = CourseSerializer4API(courseList, many=True)
            # 前端需要用来取页面 
            return JsonResponse({'errCode': '0', 'data': slzCourseList.data, 
                                 'page':page, 
                                 'totalPage':getTotalPage(pagesize,count)}, safe=False)
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)

            return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程','sysErrMsg':traceback.format_exc()}, safe=False)


    @action(detail=True,methods=['POST'], format="json")
    def GetCoursebyID(self,request,pk):
        '''
        按照id查找课程信息
        '''
        try:
            course = self.get_queryset().filter(id=pk).order_by('-update_time')[0]

            addSalesInfosOn(course, request.user)
            # course.is_buy = len(course.users.filter(id=request.user.id)) > 0
            slzCourse = CourseSerializer4API(course)
            return JsonResponse({'errCode': '0', 'data': slzCourse.data}, safe=False)
        except Exception as e:
            import traceback
            import sys
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程列表','sysErrMsg':traceback.format_exc()}, safe=False)

def addSalesInfosOnList(courseList,user):
    try:
        for course in courseList:
            addSalesInfosOn(course,user)
    except Exception as e:
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)

def addSalesInfosOn(course,user):
    # course表自带sales_num，不再查询关联表了。用于orderby。
    # course.sales_num = course.users.all().count
    try:
        if course.users.all().filter(pk=user.id):
            course.is_buy = True
        else:
            course.is_buy = False
    except Exception as e:
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)



from rest_framework.decorators import api_view, authentication_classes,permission_classes
from churchs.models import *
from church.models import *
from api.models import *
from payment.models import *
# from .utill import CICUtill
from .utill import CICUtill
from urllib.parse import unquote

from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_ARRAY
from drf_yasg.utils import swagger_auto_schema
from django.db.models.fields import CharField

@api_view(['GET'])
def delete_content(request,path=''):
    '''
    删除column下的某一个内容
    '''
    theLogger.info(path)
    ret = {'errCode': '0'}
    try:
        if request.method == 'GET':
            # data = request.data
            # key = data.get('key', '')
            if path != '':
                # {"model":"Sermon","field":'id',"value":"1"}
                theLogger.info(path)
                import json
                path = unquote(path)
                theLogger.info(path)
                path = eval(path)

                path = json.loads(path)
                theLogger.info(path)

                import ast
                model = eval(path['model'])
                
                qry = 'SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model'].lower()),path['filter'],('"%s"' % path['filter_v'] if  isinstance(model._meta.get_field(path['filter']),CharField) else path['filter_v']))
                inst1 = model.objects.raw(qry)
                 

                theLogger.info(inst1)
                theLogger.info(inst1[0].id)


                from rest_framework import serializers

                Meta = type('Meta', (object,), dict(model=model, fields='__all__'))
                theSerializer = type('theSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))
                thesz = None
                if len(inst1) == 1 :
                    thesz = theSerializer(inst1[0])
                else:
                    thesz = theSerializer(inst1,many=True)

                ret = {'errCode': '0','msg':'success','data':thesz.data}

                # >>> inst1 = model.objects.raw('SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model']),path['field'],path['value']))

            else:
                raise Exception('key must not null.')   
    except Exception as e:
        import traceback
        import sys
        ret = {'errCode': '1001', 'msg': 'there is an exception check logs'}
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    finally:
        return JsonResponse(ret, safe=False)

# @api_view(['GET'])
# @permission_classes([CICUtill.getPermissionClass()])
# def getinfo(request,path=''):
#     '''
#     path格式如下：
#     '{"model":"CustomUser","filter":"email","filter_v":"daniel@bicf.org"}'
#     model是模型的名称
#     filter是查找条件字段 filter_v 是条件值
#     '''
#     theLogger.info(path)
#     ret = {'errCode': '0'}
#     try:
#         if request.method == 'GET':
#             # data = request.data
#             # key = data.get('key', '')
#             if path != '':
#                 # {"model":"Sermon","field":'id',"value":"1"}
#                 theLogger.info(path)
#                 import json
#                 path = unquote(path)
#                 theLogger.info(path)
#                 path = eval(path)
# 
#                 path = json.loads(path)
#                 theLogger.info(path)
# 
#                 import ast
#                 model = eval(path['model'])
#                 
#                 qry = 'SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model'].lower()),path['filter'],('"%s"' % path['filter_v'] if  isinstance(model._meta.get_field(path['filter']),CharField) else path['filter_v']))
#                 inst1 = model.objects.raw(qry)
#                  
# 
#                 theLogger.info(inst1)
#                 theLogger.info(inst1[0].id)
# 
# 
#                 from rest_framework import serializers
# 
#                 Meta = type('Meta', (object,), dict(model=model, fields='__all__'))
#                 theSerializer = type('theSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))
#                 thesz = None
#                 if len(inst1) == 1 :
#                     thesz = theSerializer(inst1[0])
#                 else:
#                     thesz = theSerializer(inst1,many=True)
# 
#                 ret = {'errCode': '0','msg':'success','data':thesz.data}
# 
#                 # >>> inst1 = model.objects.raw('SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model']),path['field'],path['value']))
# 
#             else:
#                 raise Exception('key must not null.')   
#     except Exception as e:
#         import traceback
#         import sys
#         ret = {'errCode': '1001', 'msg': 'there is an exception check logs'}
#         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
#     finally:
#         return JsonResponse(ret, safe=False)
# 
# 
# @api_view(['GET'])
# @permission_classes([CICUtill.getPermissionClass()])
# def updateInfo(request,path=''):
#     '''
#     path格式如下：
#     '{"model":"CustomUser","filter":"email","filter_v":"daniel@bicf.org","field":"username","field_v":"DQ"}'
#     model是模型的名称
#     filter是查找条件字段 filter_v 是条件值
#     field是要更新的字段 field_v 是要更新的值
#     '''
#     theLogger.info(path)
#     ret = {'errCode': '0'}
#     try:
#         if request.method == 'GET':
#             # data = request.data
#             # key = data.get('key', '')
#             if path != '':
#                 # {"model":"CosmterUser","field":'username',"value":"Daniel Q"}
#                 theLogger.info(path)
#                 import json
#                 path = unquote(path)
#                 theLogger.info(path)
#                 path = eval(path)
# 
#                 path = json.loads(path)
#                 theLogger.info(path)
# 
#                 import ast
#                 model = eval(path['model'])
#                 
#                 qry = 'SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model'].lower()),path['filter'],('"%s"' % path['filter_v'] if  isinstance(model._meta.get_field(path['filter']),CharField) else path['filter_v']))
#                 inst1 = model.objects.raw(qry)
#                  
# 
#                 theLogger.info(inst1)
#                 theLogger.info(inst1[0].id)
# 
# 
#                 from rest_framework import serializers
# 
#                 Meta = type('Meta', (object,), dict(model=model, fields='__all__'))
#                 theSerializer = type('theSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))
#                 thesz = None
#                 if len(inst1) == 1 :
#                     # thesz = theSerializer(inst1[0])
#                     inst1[0].__dict__[path['field']] = path['field_v'] 
#                     inst1[0].save()
#                     thesz = theSerializer(inst1[0])
# 
#                 else:
#                     for md in inst1:
#                         md.__dict__[path['field']] = path['field_v'] 
#                         md.save()
#                     thesz = theSerializer(inst1,many=True)
# 
#                 ret = {'errCode': '0','msg':'success','data':thesz.data}
# 
#                 # >>> inst1 = model.objects.raw('SELECT * FROM %s WHERE %s = %s' % ('%s_%s' % (model.__dict__['__module__'].split('.')[0],path['model']),path['field'],path['value']))
# 
#             else:
#                 raise Exception('key must not null.')   
#     except Exception as e:
#         import traceback
#         import sys
#         ret = {'errCode': '1001', 'msg': 'there is an exception check logs'}
#         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
#     finally:
#         return JsonResponse(ret, safe=False)





         
   
