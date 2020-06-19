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


theLogger = logging.getLogger('church.all')

class ColumnContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentColumn
        fields='__all__'

class  Column_Content_ViewSet(viewsets.ModelViewSet):
    '''
    课程视图
    
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
        查找课程列表信息
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