from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from church.models import Church
from users.models import CustomUser
from django.conf import settings
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
from churchs.models.base import ContentColumn,Media

import logging 
theLogger = logging.getLogger('church.all')

'''
微页面
规则：删除，或者下架一个微页面时，要保证，至少有一个同位置的微信面在线
推广位置：app首页，主日信息首页

位置组件：
位置1 控件carousel 数据(col1)
'''

class baseChurchModel(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    create_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        app_label = 'churchs'
        verbose_name = "教会基础组件"
        verbose_name_plural = "教会基础组件"

class vpage(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    create_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    title = models.CharField(max_length=250, default='',verbose_name='标题')
    name = models.CharField(max_length=250, default='',verbose_name='名称')
    pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    APP_HOME = 1
    LORD_DAY = 2
    PROMOTE_CHOICES = (
        (APP_HOME, 'app首页'),
        (LORD_DAY, '主日信息首页')
    )
    promote_at = models.IntegerField(choices=PROMOTE_CHOICES,default=APP_HOME,verbose_name='微信面位置')
    STATUS_OPEN = 1
    STATUS_CLOSE = 2
    STATUS_CHOICES = (
        (STATUS_OPEN, '在线'),
        (STATUS_CLOSE, '下线')
    )
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_CLOSE,verbose_name='状态')

    class Meta:
        app_label = 'churchs'
        verbose_name = "微页面"
        verbose_name_plural = "微页面"

class vpage_position(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    create_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    CAROUSEL = 1
    SLIDE = 2
    LIST = 3
    TEXT = 4
    CONTROL_CHOICES = (
        (CAROUSEL, 'BANNER'),
        (SLIDE, '小图横滑'),
        (LIST, '列表'),
        (TEXT, '富文本')
    )
    control = models.IntegerField(choices=CONTROL_CHOICES,default=CAROUSEL,verbose_name='控件')
    ContentColumn = models.ForeignKey(ContentColumn,null=True,blank=True, on_delete=models.CASCADE)#position 多 <-->1  ContentColumn
    Media = models.ForeignKey(Media,null=True,blank=True, on_delete=models.CASCADE)
    content = RichTextUploadingField(null=True,blank=True,verbose_name='内容',external_plugin_resources=[('html5video',
    '/static/ckeditor/ckeditor/plugins/html5video/',
    'plugin.js'
    ),
    ])
    vpage = models.ForeignKey(vpage,null=True, on_delete=models.CASCADE)#position 多 <-->1  ContentColumn

    class Meta:
        app_label = 'churchs'
        verbose_name = "微组件"
        verbose_name_plural = "微组件"



