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
from churchs.models.base import SermonSeries,Media
from churchs.models.columnContent import ContentColumn

from datetime import datetime
import django.utils.timezone as timezone
from django.core.paginator import Paginator

import logging 
theLogger = logging.getLogger('church.all')


class Sermon(models.Model):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2

    STATUS_CHOICES = (
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '发布')
    )
    id = models.AutoField(primary_key=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='编辑员',)
    title = models.CharField(max_length=200, default='',verbose_name='标题')
    speaker = models.ForeignKey("Speaker",on_delete=models.CASCADE,default=None,verbose_name='讲员')
    cover = models.CharField(max_length=400,null=True,blank=True,verbose_name='封面')
    scripture = models.CharField(max_length=100, default='',blank=True,verbose_name='经文')
    series = models.ForeignKey(SermonSeries, on_delete=models.CASCADE,null=True,blank=True,default=None,verbose_name='讲道系列')

    # medias = GenericRelation(Media, related_query_name='Sermon',verbose_name='视听媒体')
    medias = models.ManyToManyField(Media,through='Sermon2Medias',related_name='belong_sermons')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_DRAFT,verbose_name='状态')
    class Meta:
        app_label = 'churchs'
        verbose_name = "主日信息"
        verbose_name_plural = "主日信息"

    def __str__(self):
        return '%s' % (self.title)

class Sermon2Medias(models.Model):
    MEDIA_WORSHIP = 1
    MEDIA_MC = 2
    MEDIA_SERMON = 3
    MEDIA_GIVING = 4
    MEDIA_COURSE = 5
    MEDIA_OTHER = 10


    MEDIA_KIND = (
    (MEDIA_WORSHIP,'敬拜'),
    (MEDIA_MC,'主持'),
    (MEDIA_SERMON,'讲道'),
    (MEDIA_GIVING,'奉献'),
    (MEDIA_COURSE,'课程'),
    (MEDIA_OTHER,'其它'),
    )
    Sermon = models.ForeignKey(Sermon,null=True, on_delete=models.CASCADE)
    Media = models.ForeignKey(Media,null=True, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(null=False,default=0)
    # kind = models.IntegerField(choices=MEDIA_KIND,default=MEDIA_SERMON,verbose_name='媒体种类')
    fromColumn = models.ForeignKey(ContentColumn,null=True, on_delete=models.CASCADE,verbose_name='选自专栏')

   


    class Meta:
        app_label = 'churchs'
        verbose_name = "讲道和内容关系表"
        verbose_name_plural = "讲道和内容关系表"
        ordering = ['order',]

    def __str__(self):
        return 'Sermon:%s -> Media:%s' % (self.Sermon,self.Media)


    @property
    def Media_cover(self):
        if self.Media is not None:
            return self.Media.dist_list_image
        else:
            return ''

