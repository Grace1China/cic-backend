from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from church.models import Church
from users.models import CustomUser
from django.conf import settings
from churchs.models.base import Media
import boto3
import pprint
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
import oss2
import urllib
import re
from churchs.widget import S3DirectField,AliOssDirectField,AliMediaField,MediaBaseField
from church.confs.base import get_ALIOSS_DESTINATIONS
from django.core.paginator import Paginator

import logging 
theLogger = logging.getLogger('church.all')

class ContentColumn(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    title = models.CharField(max_length=250, default='',verbose_name='标题')
    # res_path = models.CharField(max_length=250, default='',blank=True,verbose_name='资源路径')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    cover = models.CharField(max_length=400,blank=True,verbose_name='封面')
    STATUS_OPEN = 1
    STATUS_CLOSE = 2

    STATUS_CHOICES = (
        (STATUS_OPEN, '在线'),
        (STATUS_CLOSE, '下线')
    )
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_CLOSE,verbose_name='状态')
    # medias = GenericRelation(Media, related_query_name='ContentColumn',verbose_name='内容')
    medias = models.ManyToManyField(Media,through='ColumnMedias')

    hierarchy = models.CharField(max_length=400,blank=True,verbose_name='层级')
    parentColumn = models.ForeignKey('ContentColumn', on_delete=models.CASCADE,default=None,verbose_name='父专栏')
    content = RichTextUploadingField(blank=True,verbose_name='摘要',external_plugin_resources=[('html5video',
    '/static/ckeditor/ckeditor/plugins/html5video/',
    'plugin.js'
    ),
    ]) 
    # 1.2.3.4   or  3.2.1.4    or    5.1.3.4


    def medias_list(self):
        return [colMedia.Media for colMedia in ColumnMedias.objects.filter(ContentColumn=self).order_by('pub_date','order')]

    class Meta:
        app_label = 'churchs'
        verbose_name = "内容专栏"
        verbose_name_plural = "内容专栏"

    def __str__(self):
        return '%s' % (self.title)

    @property
    def dist_list_cover(self):
        if self.cover is not None and self.cover != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = 'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ = 'images')['redirecturl'],self.cover)
            return retval 
        else:
            return ''

    def _url(self,request):
        return "http://%s/blog/ccol/%d" % (request.META['HTTP_HOST'],self.id),

    @classmethod
    def getPage(cls,request=None,typ=None,series='',page=1,dkey='',skey=''): 
        try:
            if request == None:
                raise Exception(' no request is pass in.')
            user = request.user

            if (dkey != ''):
                #删除数据库
                pass

            qrset = None
            if skey != '':
                qrset = ContentColumn.objects.filter(church=user.church,title__icontains=skey).order_by('-update_time')
            else:
                theLogger.info('getPage church:%d' % user.church.id)
                qrset = ContentColumn.objects.filter(church=user.church).order_by('-update_time')
                

            total = qrset.count()
            pg = Paginator(qrset, 18)
            results = pg.page(page)

            # from  ckeditor_uploader import utils 
            # from .utils import is_valid_image_extension
            # lg.info(typ)
            # lg.info(results)
            files = []
            # dirs = set()
            for rc in results :
                # if typ == 'tuwen':
                files.append({
                    'thumb': rc.dist_list_cover,#AliyunMediaStorage.get_media_url('images', rc.image),
                    'src': rc._url(request),
                    'key':"/blog/ccol/%d" % rc.id,
                    'is_image': False,
                    'typ':typ,
                    'visible_filename': rc.title,
                })
                
                
            theLogger.info('-----get_files_from_db----files---')
            theLogger.info(files)
            return (files,total)
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e

from django.db.models.signals import pre_delete

class ColumnMedias(models.Model):
    ContentColumn = models.ForeignKey(ContentColumn,null=True, on_delete=models.CASCADE)
    Media = models.ForeignKey(Media,null=True, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(null=False,default=0)

    class Meta:
        app_label = 'churchs'
        verbose_name = "专栏内容列表"
        verbose_name_plural = "专栏内容列表"
        ordering = ['order',]

    def __str__(self):
        return 'ContentColumn:%s -> Media:%s' % (self.ContentColumn,self.Media)

    