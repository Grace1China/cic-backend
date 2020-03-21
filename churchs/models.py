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



# Create your models here.

class Venue(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.TimeField()
    address = models.CharField(max_length=255)
    addressUrl =  models.CharField(max_length=255)
    class Meta:
        verbose_name = "场地"
        verbose_name_plural = "场地"

    def __str__(self):
        return '%s' % (self.address)
    
class SermonSeries(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    title = models.CharField(max_length=32, default='',verbose_name='标题')
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

    class Meta:
        verbose_name = "讲道系列"
        verbose_name_plural = "讲道系列"

    def __str__(self):
        return '%s' % (self.title)

from .widget import S3DirectField,AliOssDirectField

class Media(models.Model):
    '''
    媒体可以用来表示不同各类的媒体，每个媒体上传到s3后，会被自动的转码。
    '''
    MEDIA_WORSHIP = 1
    MEDIA_MC = 2
    MEDIA_SERMON = 3
    MEDIA_GIVING = 4
    MEDIA_COURSE = 5
    MEDIA_OTHER = 6


    MEDIA_KIND = (
    (MEDIA_WORSHIP,'敬拜'),
    (MEDIA_MC,'主持'),
    (MEDIA_SERMON,'讲道'),
    (MEDIA_GIVING,'奉献'),
    (MEDIA_COURSE,'课程'),
    (MEDIA_OTHER,'其它'),
    )
    STATUS_NONE = 1
    STATUS_UPLOADED = 2
    STATUS_DISTRIBUTED = 3
    MEDIA_STATUS = (
        (STATUS_NONE,'还没上传媒体'),
        (STATUS_UPLOADED,'媒体已上传'),
        (STATUS_DISTRIBUTED,'媒体已转码发布')
    )
    # owner = models.ForeignKey('Sermon',null=True, blank=True,related_name='medias', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType,null=True, blank=True, on_delete=models.CASCADE, related_name='medias')
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")



    kind = models.IntegerField(choices=MEDIA_KIND,default=MEDIA_SERMON,verbose_name='媒体种类')
    title = models.CharField(max_length=120, blank=True,verbose_name='标题')  

    s3_video = S3DirectField(dest='videos', blank=True,verbose_name='视频')
    s3_video_status = models.IntegerField(choices=MEDIA_STATUS,default=STATUS_NONE,verbose_name='S3媒体状态')
    s3_SHD_URL = models.CharField(max_length=400, blank=True,verbose_name='AWS S3 超高清链接')
    s3_HD_URL = models.CharField(max_length=400, blank=True,verbose_name='AWS S3 高清链接')
    s3_SD_URL = models.CharField(max_length=400, blank=True,verbose_name='AWS S3 标清链接')
    s3_audio = S3DirectField(dest='audios', blank=True,verbose_name='AWS S3 音频')
    s3_image = S3DirectField(dest='images', blank=True,verbose_name='AWS S3 封面')
    s3_pdf = S3DirectField(dest='pdfs', blank=True,verbose_name='AWS S3 讲义')

    # alioss_video = AliOssDirectField(dest='source',fieldname='alioss_video', blank=True,verbose_name='视频')
    alioss_video = models.CharField(max_length=400, blank=True,verbose_name='视频')
    alioss_video_status = models.IntegerField(choices=MEDIA_STATUS,default=STATUS_NONE,verbose_name='视频状态')
    alioss_SHD_URL = models.CharField(max_length=400, blank=True,verbose_name='高清链接')
    alioss_HD_URL = models.CharField(max_length=400, blank=True,verbose_name='标清链接')
    alioss_SD_URL = models.CharField(max_length=400, blank=True,verbose_name='流畅链接')
    # alioss_audio = AliOssDirectField(dest='audios', fieldname='alioss_audio',blank=True,verbose_name='音频')
    # alioss_image = AliOssDirectField(dest='images',fieldname='alioss_image', blank=True,verbose_name='封面')
    # alioss_pdf = AliOssDirectField(dest='pdfs', fieldname='alioss_pdf',blank=True,verbose_name='讲义')
    alioss_audio = models.CharField(max_length=400,blank=True,verbose_name='音频')
    alioss_image = models.CharField(max_length=400,blank=True,verbose_name='封面')
    alioss_pdf = models.CharField(max_length=400,blank=True,verbose_name='讲义')
    
    content = RichTextUploadingField(blank=True,verbose_name='摘要',external_plugin_resources=[('html5video',
    '/static/ckeditor/ckeditor/plugins/html5video/',
    'plugin.js'
    ),
    ]) 


    def save(self, *args, **kwargs):
        # do_something()
        print('before save-------------------')
        print(self.alioss_video)
        print(self.alioss_image)
        self.alioss_video = urllib.parse.quote(self.alioss_video) #存储成为url比较，用于后台查找
        super().save(*args, **kwargs)  # Call the "real" save() method.
        # do_something_else()
        print(self.alioss_video)


    


    def isS3(self):
        if self.s3_video is not None and self.s3_video!='' :
            return True
        return False
    @property
    def dist_video(self):
        if self.s3_video is not None and self.s3_video!='' :
            return self.s3_video
        elif self.alioss_video is not None and self.alioss_video != '':
            return self.alioss_video
        else:
            return ''
    @property
    def dist_video_status(self):
        if self.s3_video_status is not None:
            return self.s3_video_status
        elif self.alioss_video_status is not None:
            return self.alioss_video_status
        else:
            return STATUS_NONE



    # -*- coding: utf-8 -*-

    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    # Endpoint以杭州为例，其它Region请按实际情况填写。

    # 设置此签名URL在60秒内有效。
    def getObjectKey(self,obj):
        obj = str.replace(obj, '%s.' % settings.ALIOSS_DESTINATION_BUCKET_NAME,'')
        obj = str.replace(obj, '%s/' % settings.ALIOSS_DESTINATION_ENDPOINT,'')
        obj = urllib.parse.unquote(obj)
        # pprint.PrettyPrinter(4).pprint('----------------dist_SHD_URL----------------------')
        # pprint.PrettyPrinter(4).pprint(obj)
        return obj

    @property
    def dist_SHD_URL(self):
        pprint.PrettyPrinter(4).pprint('----------------dist_SHD_URL----------------------')
        pprint.PrettyPrinter(4).pprint(self.s3_SHD_URL)
        pprint.PrettyPrinter(4).pprint(self.alioss_SHD_URL)
        if self.s3_SHD_URL is not None and self.s3_SHD_URL != '':
            return self.s3_SHD_URL
        elif self.alioss_SHD_URL is not None and self.alioss_SHD_URL != '':

            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_SHD_URL), settings.ALIOSS_EXPIRES)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_SHD_URL)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                retval = retval.split('?')[0]

            return retval #self.alioss_SHD_URL
        else:
            return ''
    def prop_dist_HD_URL(self):
        if self.s3_HD_URL is not None and self.s3_HD_URL != '':
            return self.s3_HD_URL
        elif self.alioss_HD_URL is not None and self.alioss_HD_URL != '':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_HD_URL), settings.ALIOSS_EXPIRES)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_HD_URL)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                retval = retval.split('?')[0]
            # 'http://bicf-media-destination.oss-cn-beijing.aliyuncs.com'
            retval = retval.replace('%s.%s' % (settings.ALIOSS_DESTINATION_BUCKET_NAME,settings.ALIOSS_DESTINATION_ENDPOINT),settings.MEDIABASE_PREFIX )
            return retval #self.alioss_HD_URL
        else:
            return ''
    prop_dist_HD_URL.short_description = "转码后视频(transcoded video)"
    dist_HD_URL = property(prop_dist_HD_URL)
    @property
    def dist_SD_URL(self):
        # pprint.PrettyPrinter(4).pprint('----------------dist_SD_URL----------------------')
        # pprint.PrettyPrinter(4).pprint(self.s3_SD_URL)
        # pprint.PrettyPrinter(4).pprint(self.alioss_SD_URL)
        if self.s3_SD_URL is not None and self.s3_SD_URL != '':
            return self.s3_SD_URL
        elif self.alioss_SD_URL is not None and self.alioss_SD_URL != '':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_SD_URL), settings.ALIOSS_EXPIRES)
            # pprint.PrettyPrinter(4).pprint(retval)
            # pprint.PrettyPrinter(4).pprint(bucket.get_object_acl(self.getObjectKey(self.alioss_SD_URL)).acl)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_SD_URL)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                retval = retval.split('?')[0]
            return retval #self.alioss_SD_URL
        else:
            return ''
    @property
    def dist_audio(self):
        if self.s3_audio is not None and self.s3_audio != '':
            return self.s3_audio
        elif self.alioss_audio is not None and self.alioss_audio != '':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_audio), settings.ALIOSS_EXPIRES)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_audio)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                retval = retval.split('?')[0]
            return retval  #self.alioss_audio
        else:
            return ''
    @property
    def dist_image(self):
        if self.s3_image is not None and self.s3_image != '':
            return self.s3_image
        elif self.alioss_image is not None and self.alioss_image != '':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_image)).acl == 'private':
                bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
                retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_image), settings.ALIOSS_EXPIRES)
                if bucket.get_object_acl(self.getObjectKey(self.alioss_image)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                    retval = retval.split('?')[0]
                return retval #self.alioss_pdf
            else:
                return 'http://%s.%s/%s' % (settings.ALIOSS_DESTINATION_BUCKET_NAME,settings.ALIOSS_DESTINATION_LOCATION,self.getObjectKey(self.alioss_image))
            
            return retval #self.alioss_image
        else:
            return ''
    @property
    def dist_pdf(self):
        if self.s3_pdf is not None and self.s3_pdf != '':
            return self.s3_pdf
        elif self.alioss_pdf is not None and self.alioss_pdf !='':
            auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
            if bucket.get_object_acl(self.getObjectKey(self.alioss_pdf)).acl == 'private':
                bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATION_ENDPOINT, settings.ALIOSS_DESTINATION_BUCKET_NAME)
                retval = bucket.sign_url('GET', self.getObjectKey(self.alioss_pdf), settings.ALIOSS_EXPIRES)
                if bucket.get_object_acl(self.getObjectKey(self.alioss_pdf)).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
                    retval = retval.split('?')[0]
                return retval #self.alioss_pdf
            else:
                return 'http://%s.%s/%s' % (settings.ALIOSS_DESTINATION_BUCKET_NAME,settings.ALIOSS_DESTINATION_LOCATION,self.getObjectKey(self.alioss_pdf))
        else:
            return ''


   
    

    class Meta:
        verbose_name = "视听媒体"
        verbose_name_plural = "视听媒体"

    def __str__(self):
        return '%s' % (self.title)



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
    scripture = models.CharField(max_length=100, default='',blank=True,verbose_name='经文')
    series = models.ForeignKey(SermonSeries, on_delete=models.CASCADE,null=True,blank=True,default=None,verbose_name='讲道系列')

    medias = GenericRelation(Media, related_query_name='Sermon',verbose_name='视听媒体')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_DRAFT,verbose_name='状态')



    class Meta:
        verbose_name = "主日信息"
        verbose_name_plural = "主日信息"

    def __str__(self):
        return '%s' % (self.title)
                
    


class WeeklyReport(models.Model):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2
    STATUS_TEST = 3

    STATUS_CHOICES = (
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '发布'),
        (STATUS_TEST, '测试')
    )
    church = models.ForeignKey(Church, on_delete=models.CASCADE,null=True, blank=True,default=None,verbose_name='教会')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='作者')
    title = models.CharField(max_length=32,default='',verbose_name='标题')
    image = models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='封面')
    #todo 
    content = RichTextUploadingField(null=True, blank=True,verbose_name='内容')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(auto_now_add=True,null=True, blank=True,editable=True,verbose_name='发布时间')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_DRAFT,verbose_name='状态')
    class Meta:
        verbose_name = "周报"
        verbose_name_plural = "周报"

    def __str__(self):
        return '%s' % (self.title)



class Team(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2

    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    
    church = models.ForeignKey(Church,null=True,  on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_INITED
    )
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "小组"
        verbose_name_plural = "小组"
    def __str__(self):
        return self.name


class Donation(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,verbose_name='会友信息')
    amount = models.DecimalField(decimal_places=10, max_digits=12,verbose_name='数量')
    pay_type = models.IntegerField(verbose_name='支付类型')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name='更新时间')
    pay_time = models.DateTimeField(null=True,verbose_name='支付时间')
    class Meta:
        verbose_name = "奉献"
        verbose_name_plural = "奉献"
    def __str__(self):
        return '支付类型%d' % (self.pay_type)





class Speaker(models.Model):
    # church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    churchs = models.ManyToManyField(to=Church,default=None,  blank=True,verbose_name='教会')
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    introduction = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True) 
    class Meta:
        verbose_name = "讲员"
        verbose_name_plural = "讲员"
    def __str__(self):
        return '%s' % (self.name)


class Meeting(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    speaker = models.ForeignKey("Speaker",null=True,  on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    time = models.DateTimeField
    description = models.CharField(max_length=255)
    # content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "聚会"
        verbose_name_plural = "聚会"
    def __str__(self):
        return '%s' % (self.name)
    
class BibleStudy(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    speaker = models.ForeignKey("Speaker",null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "灵修"
        verbose_name_plural = "灵修"
    def __str__(self):
        return '%s' % (self.name)

    
    
class BibleStudyComment(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    user = models.ForeignKey(CustomUser,null=True,  on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "灵修评论"
        verbose_name_plural = "灵修评论"
    def __str__(self):
        return '%s' % (self.content)


    




