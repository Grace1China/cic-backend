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
from churchs.models import Media
from rest_framework import serializers,viewsets
from rest_framework.decorators import action
from django.http import HttpResponse, JsonResponse
from .utill import timeSpan
from datetime import datetime as dd
from .serializers import MediaSerializer4ListAPI,MediaSerializer4RefreshListAPI


theLogger = logging.getLogger('church.all')

class ColumnContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentColumn
        fields='__all__'
        depth = 1

class  Column_Content_ViewSet(viewsets.ModelViewSet):
    '''
    专栏内容视频
    
    '''
    from churchs.models import ContentColumn
    # from church.models import Course
    # from django.db.models import Prefetch
    
    queryset = ContentColumn.objects
    serializer_class=ColumnContentSerializer
    # permission_classes=[AllowAny] user url decoratios staff_required

    @action(detail=True,methods=['get','post'], format="json")
    def delete_content_of_column(self,request):
        '''
        删除某一专栏的内容
        '''
        try:
            # theLogger.info('start GetCourseList-------------')
            tmspan = timeSpan(dd.now())
            

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                theLogger.info(data)
                columnid = int(data.get('columnid',-1))
                contentid = int(data.get('contentid',-1))  
                theLogger.info('columnid:%dcontentid:%d' % (columnid,contentid))
                if columnid < 0 or contentid < 0:
                    raise Exception('column id or content id is wrong.')  

                qr = self.get_queryset()
                col = qr.get(id=columnid)
                if col is None:
                    raise Exception('column is not find')

                media = Media.objects.get(id=contentid)
                if media is None:
                    raise Exception('content media is not find')

                col.medias.remove(media)

                return JsonResponse({'errCode': '0', 'msg':'delete content(%d) from column(%d)' % (columnid,contentid)}, safe=False)
           
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg':'delete content err','sysErrMsg':traceback.format_exc()}, safe=False)


    @action(detail=True,methods=['get','post'], format="json")
    def GetColumnByID(self,request):
        '''
        查找某一专栏内容列表
        '''
        try:
            # theLogger.info('start GetCourseList-------------')
            tmspan = timeSpan(dd.now())

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                theLogger.info(data)
                columnid = int(data.get('columnid',-1))
                # contentid = int(data.get('contentid',-1))   or contentid < 0
                theLogger.info('columnid:%d' % columnid)
                if columnid < 0 :
                    columnid = request.user.church.Lord_Day_column.id
                    # raise Exception('column id is wrong.')  

                qr = self.get_queryset()
                col = qr.get(id=columnid)
                if col is None:
                    raise Exception('column is not find')
                # col.medias.all()
                # 这里需要返回一个专栏的所有内容的列表，并序列化返回
                slzCol = self.get_serializer(col)
                return JsonResponse({'errCode': '0', 'msg':'column %ds content here' % (columnid),'data': slzCol.data}, safe=False)
           
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg':'get column content err','sysErrMsg':traceback.format_exc()}, safe=False)

    @action(detail=True,methods=['get','post'], format="json")
    def GetColumnMediasByColumnID(self,request):
        '''
        查找某一专栏内容列表
        '''
        try:
            # theLogger.info('start GetCourseList-------------')
            tmspan = timeSpan(dd.now())

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                theLogger.info(data)
                columnid = int(data.get('columnid',-1))
                # contentid = int(data.get('contentid',-1))   or contentid < 0
                theLogger.info('columnid:%d' % columnid)
                if columnid < 0 :
                    columnid = request.user.church.Lord_Day_column.id
                    # raise Exception('column id is wrong.')  

                

                page = request.GET.get('page',1)
                pageSize = request.GET.get('pagesize',20)

                qry = self.get_queryset()
                col = qry.get(id=columnid)

                paginator = Paginator(col.medias.all(), pageSize) # Show 25 contacts per page

                if col is None:
                    raise Exception('column is not find')
                # col.medias.all()
                # 这里需要返回一个专栏的所有内容的列表，并序列化返回
                slzMedias = MediaSerializer4RefreshListAPI(paginator.get_page(page),many=True)
                return JsonResponse({'errCode': '0', 'msg':'column %ds content here' % (columnid),'data': slzMedias.data}, safe=False)
           
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg':'get column content err','sysErrMsg':traceback.format_exc()}, safe=False)
    # @action(detail=True,methods=['POST'], format="json")
    # def GetCoursebyID(self,request,pk):
    #     '''
    #     按照id查找课程信息
    #     '''
    #     try:
    #         course = self.get_queryset().filter(id=pk).order_by('-update_time')[0]

    #         addSalesInfosOn(course, request.user)
    #         slzCourse = CourseSerializer4API(course)
    #         return JsonResponse({'errCode': '0', 'data': slzCourse.data}, safe=False)
    #     except Exception as e:
    #         import traceback
    #         import sys
    #         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #         return JsonResponse({'errCode': '1001', 'data': None,'msg':'没有课程列表','sysErrMsg':traceback.format_exc()}, safe=False)