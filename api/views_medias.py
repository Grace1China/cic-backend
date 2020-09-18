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

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields='__all__'
        # depth = 1

class  Media_ViewSet(viewsets.ModelViewSet):
    '''
    专栏内容视频
    
    '''
    # from churchs.models import Media
    # from church.models import Course
    # from django.db.models import Prefetch
    
    queryset = Media.objects
    serializer_class=MediaSerializer

    @action(detail=True,methods=['get','post'], format="json")
    def GetMediaByID(self,request):
        '''
        查找某一专栏内容列表
        '''
        try:
            # theLogger.info('start GetCourseList-------------')
            tmspan = timeSpan(dd.now())

            if(request.META['REQUEST_METHOD']  == 'GET'):
                data = request.GET
                theLogger.info(data)
                mediaid = int(data.get('mediaid',-1))
                theLogger.info('mediaid:%d' % mediaid)
                if mediaid < 0 :
                    raise Exception('meida id is wrong.')  

                qr = self.get_queryset()
                media = qr.get(id=mediaid)
                if media is None:
                    raise Exception('media is not find')
                # col.medias.all()
                # 这里需要返回一个专栏的所有内容的列表，并序列化返回
                slzMedia = self.get_serializer(media)
                return JsonResponse({'errCode': '0', 'msg':'Media %ds content here' % (mediaid),'data': slzMedia.data}, safe=False)
           
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg':'get column content err','sysErrMsg':traceback.format_exc()}, safe=False)

    # @action(detail=True,methods=['get','post'], format="json")
    # def GetColumnMediasByColumnID(self,request):
    #     '''
    #     查找某一专栏内容列表
    #     '''
    #     try:
    #         # theLogger.info('start GetCourseList-------------')
    #         tmspan = timeSpan(dd.now())

    #         if(request.META['REQUEST_METHOD']  == 'GET'):
    #             data = request.GET
    #             theLogger.info(data)
    #             columnid = int(data.get('columnid',-1))
    #             # contentid = int(data.get('contentid',-1))   or contentid < 0
    #             theLogger.info('columnid:%d' % columnid)
    #             if columnid < 0 :
    #                 columnid = request.user.church.Lord_Day_column.id
    #                 # raise Exception('column id is wrong.')  

                

    #             page = request.GET.get('page',1)
    #             pageSize = request.GET.get('pagesize',20)

    #             qry = self.get_queryset()
    #             col = qry.get(id=columnid)

    #             paginator = Paginator(col.medias.order_by('-pub_time').all(), pageSize) # Show 25 contacts per page

    #             if col is None:
    #                 raise Exception('column is not find')
    #             # col.medias.all()
    #             # 这里需要返回一个专栏的所有内容的列表，并序列化返回
    #             slzMedias = MediaSerializer4RefreshListAPI(paginator.get_page(page),many=True)
    #             return JsonResponse({'errCode': '0', 'msg':'column %ds content here' % (columnid),'data': slzMedias.data,'page':page,'totalPage':paginator.num_pages}, safe=False)
           
    #     except Exception as e:
    #         import traceback
    #         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #         return JsonResponse({'errCode': '1001', 'msg':'get column content err','sysErrMsg':traceback.format_exc()}, safe=False)


    # @action(detail=True,methods=['get','post'], format="json")
    # def GetColumnMediasByColumnTitle(self,request):
    #     '''
    #     查找某一专栏内容列表
    #     '''
    #     try:
    #         # theLogger.info('start GetCourseList-------------')
    #         tmspan = timeSpan(dd.now())

    #         if(request.META['REQUEST_METHOD']  == 'GET'):
    #             data = request.GET
    #             theLogger.info(data)
    #             columntitle = data.get('title','')
    #             # contentid = int(data.get('contentid',-1))   or contentid < 0
    #             theLogger.info('column title:%s' % columntitle)
    #             if columntitle == '' :
    #                 raise Exception('column title is wrong.')  

                

    #             page = request.GET.get('page',1)
    #             pageSize = request.GET.get('pagesize',20)

    #             qry = self.get_queryset()
    #             col = qry.filter(title__contains=columntitle)
    #             theLogger.info(col)
    #             if(len(col)<=0):
    #                 raise Exception('there is no such column : %s' % columntitle)  
    #             aCol = col[0]

    #             paginator = Paginator(aCol.medias.order_by('-pub_time').all(), pageSize) # Show 25 contacts per page

    #             # if col is None:
    #             #     raise Exception('column is not find')
    #             # # col.medias.all()
    #             # 这里需要返回一个专栏的所有内容的列表，并序列化返回
    #             slzMedias = MediaSerializer4RefreshListAPI(paginator.get_page(page),many=True)
    #             return JsonResponse({'errCode': '0', 'msg':'column %s content here' % (columntitle),'data': slzMedias.data,'page':page,'totalPage':paginator.num_pages}, safe=False)
           
    #     except Exception as e:
    #         import traceback
    #         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #         return JsonResponse({'errCode': '1001', 'msg':'get column content err','sysErrMsg':traceback.format_exc()}, safe=False)
    