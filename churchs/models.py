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
from .widget import S3DirectField,AliOssDirectField,AliMediaField,MediaBaseField

import logging 
theLogger = logging.getLogger('church.all')

class test1(models.Model):
    image = MediaBaseField(max_length=400,blank=True,verbose_name='封面')

# Create your models here.

class Venue(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.TimeField()
    address = models.CharField(max_length=255)
    addressUrl =  models.CharField(max_length=255)
    createdby = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='创建者')
    class Meta:
        verbose_name = "场地"
        verbose_name_plural = "场地"

    def __str__(self):
        return '%s' % (self.address)
    
class SermonSeries(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='用户')
    title = models.CharField(max_length=250, default='',verbose_name='标题')
    res_path = models.CharField(max_length=250, default='',blank=True,verbose_name='资源路径')
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
        verbose_name = "专栏系列"
        verbose_name_plural = "专栏系列"

    def __str__(self):
        return '%s' % (self.title)
from django.db.models.signals import pre_save  
def create_oss_dir(sender,instance,update_fields,**kwargs):
    '''
    要在创建系列实例之前，把oss的目录先创建好。先分配资源，然后生成对象。分配了资源，没有保存对象,下次对象生成，依然用这个资源
    '''
    try:
        if instance.res_path  == '' or instance.res_path is None or instance.res_path=='--empty--':
            ct = SermonSeries.objects.filter(church__exact = instance.church).count()
            # if ct <= 0:
            #     instance.res_path = '/'
            # else:
            theLogger.info('----create_oss_dir-------')
            instance.res_path = 'series_%d' % (ct+1)
            #删除这一段的原因，是因为，一个原则，只在一处存储系列的集合关系。

            # path = '%s/%s' % (instance.church.code,instance.res_path)
            # auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
            # d = settings.ALIOSS_DESTINATIONS
            # theLogger.info('-----------create_oss_dir------------')
            # theLogger.info(path)
            
            # dictB = dict()
            # for k,v in d.items():
            #     if v['bucket'] not in dictB:
            #         dictB[v['bucket']] = v['endpoint.acc']
                

            # for k in dictB:
            #     # 每一个类型的文件都有一个系列存储位置
            #     theLogger.info('dictB[%s]=%s' % (k,dictB[k]))
            #     b = oss2.Bucket(auth, dictB[k], k)
            #     theLogger.info(b)
            #     r  = b.list_objects(path,max_keys=1)
            #     theLogger.info(r)
            #     l = len(r.object_list)
            #     theLogger.info(l)
            #     if l <= 0 :
            #         # 不存在这个prefix，可以保存一个readme,来建立这个前缀
            #         b.put_object('%s/readme.md' % path,'this is for series:%s' % instance.res_path)
            #     else:
            #         # 存在 检测一下 有没有readme, 以及是不是这个sereis的readme
            #         if not b.object_exists('%s/readme.md' % path):
            #             raise Exception('the resource path:%s is exists but no readme setting for sereis: %s' % (path, instance.res_path))   
            #         r = b.get_object('%s/readme.md' % path) 
            #         cnt = str(r.read(), encoding = "utf-8")
            #         if cnt != 'this is for series:%s' % instance.res_path:
            #             raise Exception('the resource path:%s is exists and it is not for series: %s' % (path, instance.res_path))                
    except Exception as e:
        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
        raise e
    # finally:
        # pass

pre_save.connect(create_oss_dir, sender=SermonSeries)

class MediaFile(models.Model):
    '''
    用来存储oss的单个媒体文件
    '''  

    STATUS_UPLOADED = 1
    STATUS_TRANSCODING = 2
    STATUS_TRANSCODED = 3
    MEDIA_STATUS = (
        (STATUS_UPLOADED,'上传完成'),
        (STATUS_TRANSCODING,'正在转码'),
        (STATUS_TRANSCODED,'转码发布')
    )

    id = models.AutoField(primary_key=True)
    # church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None,verbose_name='教会')
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=None,verbose_name='编辑员',)
    name = models.CharField(max_length=200, default='',unique=True,verbose_name='oss存储key GUID') #目前保持唯一。guid也应该是唯一
    origin_name = models.CharField(max_length=200, default='',verbose_name='媒体原有文件名')
    endpoint = models.CharField(max_length=200, default='',verbose_name='桶地址')
    bucket = models.CharField(max_length=200, default='',verbose_name='桶名称')

    series_prefix = models.CharField(max_length=200, default='/',verbose_name='教会存储目录')
    church_prefix = models.CharField(max_length=200, default='L3',verbose_name='教会存储目录')
    mime_type = models.CharField(max_length=50, default='',verbose_name='媒体类型')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    video_file_status = models.IntegerField(choices=MEDIA_STATUS,default=STATUS_UPLOADED,verbose_name='视频文件状态')
    video_file_tcinfo = models.CharField(max_length=1000,null=True,verbose_name='视频转码文件')
    # pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    # status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_DRAFT,verbose_name='状态')


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
    alioss_video = MediaBaseField(max_length=400,blank=True,verbose_name='视频')
    
    # alioss_video = models.CharField(max_length=400, blank=True,verbose_name='视频')
    alioss_video_status = models.IntegerField(choices=MEDIA_STATUS,default=STATUS_NONE,verbose_name='视频状态')
    alioss_SHD_URL = models.CharField(max_length=400, blank=True,verbose_name='高清链接')
    alioss_HD_URL = models.CharField(max_length=400, blank=True,verbose_name='标清链接')
    alioss_SD_URL = models.CharField(max_length=400, blank=True,verbose_name='流畅链接')
    # alioss_audio = AliOssDirectField(dest='audios', fieldname='alioss_audio',blank=True,verbose_name='音频')
    # alioss_image = AliOssDirectField(dest='images',fieldname='alioss_image', blank=True,verbose_name='封面')
    # alioss_pdf = AliOssDirectField(dest='pdfs', fieldname='alioss_pdf',blank=True,verbose_name='讲义')
    alioss_audio = models.CharField(max_length=400,blank=True,verbose_name='音频')
    # alioss_image = models.CharField(max_length=400,blank=True,verbose_name='封面')
    alioss_image = MediaBaseField(max_length=400,blank=True,verbose_name='封面')
    alioss_pdf = models.CharField(max_length=400,blank=True,verbose_name='讲义')
    
    content = RichTextUploadingField(blank=True,verbose_name='摘要',external_plugin_resources=[('html5video',
    '/static/ckeditor/ckeditor/plugins/html5video/',
    'plugin.js'
    ),
    ]) 


    def save(self, *args, **kwargs):
        # do_something()
        theLogger.info(self.alioss_video)
        # self.alioss_video = urllib.parse.quote(self.alioss_video) #存储成为url比较，用于后台查找
        theLogger.info(self.alioss_video)
        super().save(*args, **kwargs)  # Call the "real" save() method.
        # do_something_else()


    


    def isS3(self):
        if self.s3_video is not None and self.s3_video!='' :
            return True
        return False
    @property
    def dist_video(self):
        if self.s3_video is not None and self.s3_video!='' :
            return self.s3_video
        elif self.alioss_video is not None and self.alioss_video != '':
            # return self.alioss_video
            retval = self.getMediaUrl(self.alioss_video)
            return retval
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
        return obj

    def getMediaUrl(self,key,dest="source"):
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        theLogger.info(bucket)

        theLogger.info(key)
        # key = re.sub(r'(^[^\/]*/)', r'\1mp4-hd/',key)  #"ci/p4/3.jpg"
        # key = re.sub(r'\..*$', r'.mp4/',key)
        # theLogger.info(key)
        # key = urllib.parse.unquote(key)

            #如果是视频在目标存储桶中，就要把转码的目录加入进来

        if not bucket.object_exists(key) :
            return "" #不存在文件 返回空

        retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)

        if bucket.get_object_acl(key).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
            retval = retval.split('?')[0]
        else:
            pass
            #通过nginx来转发，国内国外请求，可以减少费用。但是目前还不是很稳定，所以等后台有了动态配置功能后再实施？

        return retval
            

    def getTransCodedMediaUrl(self,key,coderatio='mp4-hd'):
        '''
        转码的媒体的url找出来。
        '''
        dest = 'destination'
        auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
        bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
        theLogger.info(bucket)
        if coderatio == '':
            raise Exception('bucket and transcode directory not right.')
        theLogger.info(key)
        key = re.sub(r'(^[^\/]*/)', (r'\1%s/' % coderatio),key)  #"ci/p4/3.jpg"
        key = re.sub(r'\..*$', r'.mp4',key)
        theLogger.info(key)
        key = urllib.parse.unquote(key)
        theLogger.info(key)

        theLogger.info(bucket.object_exists(key))

            #如果是视频在目标存储桶中，就要把转码的目录加入进来

        if not bucket.object_exists(key) :
            return "" #不存在文件 返回空

        retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
        theLogger.info(retval)
        theLogger.info(bucket.get_object_acl(key).acl)
        theLogger.info(oss2.OBJECT_ACL_PUBLIC_READ)
        if bucket.get_object_acl(key).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
            retval = retval.split('?')[0]
        else:
            pass
            #通过nginx来转发，国内国外请求，可以减少费用。但是目前还不是很稳定，所以等后台有了动态配置功能后再实施？
        theLogger.info(retval)
        

        return retval
            
        



    #----------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def dist_SHD_URL_deprecate(self):
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
    @property
    def dist_SHD_URL(self):
        if self.s3_SHD_URL is not None and self.s3_SHD_URL != '':
            return self.s3_SHD_URL
        elif self.alioss_video is not None and self.alioss_video != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            theLogger.info('self.alioss_video:%s' % self.alioss_video)
            retval = self.getTransCodedMediaUrl(self.alioss_video,coderatio='mp4-hd')
            theLogger.info('retval:%s' % retval)

            return retval #self.alioss_SHD_URL
        else:
            return ''
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def prop_dist_HD_URL(self):
        if self.s3_HD_URL is not None and self.s3_HD_URL != '':
            return self.s3_HD_URL
        elif self.alioss_video is not None and self.alioss_video != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = self.getTransCodedMediaUrl(self.alioss_video,coderatio='mp4-sd')
            theLogger.info('retval:%s' % retval)

            return retval #self.alioss_SHD_URL
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
        elif self.alioss_video is not None and self.alioss_video != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = self.getTransCodedMediaUrl(self.alioss_video,coderatio='mp4-ld')
            theLogger.info('retval:%s' % retval)

            return retval #self.alioss_SHD_URL
        else:
            return ''
    @property
    def dist_audio(self):
        if self.s3_audio is not None and self.s3_audio != '':
            return self.s3_audio
        elif self.alioss_audio is not None and self.alioss_audio != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = self.getMediaUrl(self.alioss_audio,dest='audios')
            return retval 
        else:
            return ''
    @property
    def dist_image(self):
        if self.s3_image is not None and self.s3_image != '':
            return self.s3_image
        elif self.alioss_image is not None and self.alioss_image != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = self.getMediaUrl(self.alioss_image,dest='images')
            return retval 
        else:
            return ''
    @property
    def dist_pdf(self):
        if self.s3_pdf is not None and self.s3_pdf != '':
            return self.s3_pdf
        elif self.alioss_pdf is not None and self.alioss_pdf != '':
            #在目标桶是否存在 key,存在还要看下是否是可读，如果公共可读，直接返回url。如果不可读，返回签名的url
            retval = self.getMediaUrl(self.alioss_pdf,dest='pdfs')
            return retval 
        else:
            return ''


   
    

    class Meta:
        verbose_name = "视听媒体"
        verbose_name_plural = "视听媒体"

    def __str__(self):
        return '%s' % (self.title)


from church.alioss_storage_backends_v2 import AliyunMediaStorage,AliyunStaticStorage

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
    cover = models.ImageField(storage=AliyunMediaStorage(), null=True, blank=True,verbose_name='海报封面')
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
    content = RichTextUploadingField(null=True, blank=True,verbose_name='内容',external_plugin_resources=[('html5video','/static/ckeditor/ckeditor/plugins/html5video/','plugin.js'),('abbr','/static/ckeditor/ckeditor/plugins/abbr/','plugin.js')
    
    ]) 
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
    profile = AliMediaField(max_length=255,null=True,verbose_name='照片')
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


    




