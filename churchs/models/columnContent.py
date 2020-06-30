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
    STATUS_OPEN = 1
    STATUS_CLOSE = 2

    STATUS_CHOICES = (
        (STATUS_OPEN, '在线'),
        (STATUS_CLOSE, '下线')
    )
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_CLOSE,verbose_name='状态')
    # medias = GenericRelation(Media, related_query_name='ContentColumn',verbose_name='内容')
    medias = models.ManyToManyField(Media,through='ColumnMedias')

    def medias_list(self):
        return [colMedia.Media for colMedia in ColumnMedias.objects.filter(ContentColumn=self).order_by('order')]

    class Meta:
        app_label = 'churchs'
        verbose_name = "内容专栏"
        verbose_name_plural = "内容专栏"

    def __str__(self):
        return '%s' % (self.title)

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