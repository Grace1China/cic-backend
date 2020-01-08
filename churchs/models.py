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
    MEDIA_OTHER = 5


    MEDIA_KIND = (
    (MEDIA_WORSHIP,'敬拜'),
    (MEDIA_MC,'主持'),
    (MEDIA_SERMON,'讲道'),
    (MEDIA_GIVING,'奉献'),
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
    owner = models.ForeignKey('Sermon',null=True, blank=True,related_name='medias', on_delete=models.CASCADE)
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

    alioss_video = AliOssDirectField(dest='videos',fieldname='alioss_video', blank=True,verbose_name='阿里云视频')
    alioss_video_status = models.IntegerField(choices=MEDIA_STATUS,default=STATUS_NONE,verbose_name='Aliyun媒体状态')
    alioss_SHD_URL = models.CharField(max_length=400, blank=True,verbose_name='Aliyun oss 超高清链接')
    alioss_HD_URL = models.CharField(max_length=400, blank=True,verbose_name='Aliyun oss 高清链接')
    alioss_SD_URL = models.CharField(max_length=400, blank=True,verbose_name='Aliyun oss 标清链接')
    alioss_audio = AliOssDirectField(dest='audios', fieldname='alioss_audio',blank=True,verbose_name='Aliyun oss 音频')
    alioss_image = AliOssDirectField(dest='images',fieldname='alioss_image', blank=True,verbose_name='Aliyun oss 封面')
    alioss_pdf = AliOssDirectField(dest='pdfs', fieldname='alioss_pdf',blank=True,verbose_name='Aliyun oss 讲义')
    
    content = models.TextField(blank=True,verbose_name='摘要') 
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
    @property
    def dist_SHD_URL(self):
        pprint.PrettyPrinter(4).pprint('----------------dist_SHD_URL----------------------')
        pprint.PrettyPrinter(4).pprint(self.s3_SHD_URL)
        pprint.PrettyPrinter(4).pprint(self.alioss_SHD_URL)
        if self.s3_SHD_URL is not None and self.s3_SHD_URL != '':
            return self.s3_SHD_URL
        elif self.alioss_SHD_URL is not None and self.alioss_SHD_URL != '':
            return self.alioss_SHD_URL
        else:
            return ''
    @property
    def dist_HD_URL(self):
        if self.s3_HD_URL is not None and self.s3_HD_URL != '':
            return self.s3_HD_URL
        elif self.alioss_HD_URL is not None and self.alioss_HD_URL != '':
            return self.alioss_HD_URL
        else:
            return ''
    @property
    def dist_SD_URL(self):
        pprint.PrettyPrinter(4).pprint('----------------dist_SD_URL----------------------')
        pprint.PrettyPrinter(4).pprint(self.s3_SD_URL)
        pprint.PrettyPrinter(4).pprint(self.alioss_SD_URL)
        if self.s3_SD_URL is not None and self.s3_SD_URL != '':
            return self.s3_SD_URL
        elif self.alioss_SD_URL is not None and self.alioss_SD_URL != '':
            return self.alioss_SD_URL
        else:
            return ''
    @property
    def dist_audio(self):
        if self.s3_audio is not None and self.s3_audio != '':
            return self.s3_audio
        elif self.alioss_audio is not None and self.alioss_audio != '':
            return self.alioss_audio
        else:
            return ''
    @property
    def dist_image(self):
        if self.s3_image is not None and self.s3_image != '':
            return self.s3_image
        elif self.alioss_image is not None and self.alioss_image != '':
            return self.alioss_image
        else:
            return ''
    @property
    def dist_pdf(self):
        if self.s3_pdf is not None and self.s3_pdf != '':
            return self.s3_pdf
        elif self.alioss_pdf is not None and self.alioss_pdf !='':
            return self.alioss_pdf
        else:
            return ''
    @property
    def image_presigned_url(self):
        url = str(self.dist_image)
        if url == None or len(url) == 0:
            return ''
        # import logging
        # logging.debug(url)
        pprint.PrettyPrinter(indent=4).pprint(url)
        # pprint.pre
        import logging
        logging.debug(settings.AWS_STORAGE_BUCKET_NAME)
        if url.index(settings.AWS_STORAGE_BUCKET_NAME) >= 0:
            url = url.split('%s/' % settings.AWS_STORAGE_BUCKET_NAME)[1]
            s3_client = boto3.client('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            try:
                response = s3_client.generate_presigned_url('get_object',Params={ 'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': url },ExpiresIn=3600)
            except Exception as e:
                return str(e)
            return response
        else:
            return url
    @property    
    def pdf_presigned_url(self):
        url = str(self.dist_image)
        if url == None or len(url) == 0:
            return ''
        # import logging
        # logging.debug(url)
        # logging.debug(settings.AWS_STORAGE_BUCKET_NAME)
        if url.index(settings.AWS_STORAGE_BUCKET_NAME) >= 0:
            url = url.split('%s/' % settings.AWS_STORAGE_BUCKET_NAME)[1]
            s3_client = boto3.client('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            try:
                response = s3_client.generate_presigned_url('get_object',Params={ 'Bucket': settings.AWS_STORAGE_BUCKET_NAME,'Key': url },ExpiresIn=3600)
            except Exception as e:
                return str(e)
            return response
        else:
            return url
    

    class Meta:
        verbose_name = "视听媒体"
        verbose_name_plural = "视听媒体"

    def __str__(self):
        return '%s' % (self.title)

class ossMedia(models.Model):
    '''
    存储oss相关信息，可能是s3,可能是alioss,有原文件信息，也有发布以后的媒体信息
    '''



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
    title = models.CharField(max_length=32, default='',verbose_name='标题')
    # date = models.DateField(verbose_name='日期')
   
    # description = models.TextField(null=True, blank=True,verbose_name='敬拜')
    # pdf = models.FileField(storage=PrivateMediaStorage(),null=True, blank=True,verbose_name='讲义')
    speaker = models.ForeignKey("Speaker",on_delete=models.CASCADE,default=None,verbose_name='讲员')
    scripture = models.CharField(max_length=100, default='',verbose_name='经文')
    series = models.ForeignKey(SermonSeries, on_delete=models.CASCADE,null=True,default=None,verbose_name='讲道系列')
    # cover = models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='封面')
    # worshipvideo = models.FileField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='敬拜')
    # worshipnote = models.TextField(null=True, blank=True,verbose_name='敬拜歌单')
    # mcvideo = models.FileField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='主持')
    # mcnote = models.TextField(null=True, blank=True,verbose_name='主持摘要')
    # sermonvideo = models.FileField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='讲道')
    # sermonvnote = models.TextField(null=True, blank=True,verbose_name='讲道摘要')
    # givingvideo = models.FileField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='奉献')
    # givingnote = models.TextField(null=True, blank=True,verbose_name='奉献摘要')
    # worshiptext = models.TextField(u'敬拜', null=True, blank=True)
    # content = RichTextUploadingField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True,verbose_name='发布时间')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_DRAFT,verbose_name='状态')

    # sermonfile = models.ForeignKey("file2s3",on_delete=models.CASCADE,default=None,related_name="sermon2s3",verbose_name='讲道')


    class Meta:
        verbose_name = "主日信息"
        verbose_name_plural = "主日信息"

    def __str__(self):
        return '%s' % (self.title)

# class file2s3(models.Model):
#     summary = models.TextField(max_length=255, blank=True,verbose_name='摘要')
#     file = models.FileField(storage=PrivateMediaStorage(),null=True, blank=True,verbose_name='文件')
#     cover = models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='封面')
#     uploaded_at = models.DateTimeField(auto_now_add=True)


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

# class Member(models.Model):
#     email = models.EmailField(max_length=64,verbose_name='email地址')
#     phone = models.CharField(max_length=16,verbose_name='电话')
#     password = models.CharField(max_length=256,verbose_name='密码')
#     create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
#     class Meta:
#         verbose_name = "会友"
#         verbose_name_plural = "会友"
#     def __str__(self):
#         return '%s' % (self.title)

class Team(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2

    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
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


# class userProfile(models.Model):
#     ROLE_MEMBER = 1
#     ROLE_GROUPLEAD = 2
#     ROLE_CHURCHLEAD = 3


#     ROLE_CHOICES = (
#         (ROLE_MEMBER ,'会员'),
#         (ROLE_GROUPLEAD , '组长'),
#         (ROLE_CHURCHLEAD ,'教会管理员')
#     )
#     user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="userProfile",verbose_name='用户')
#     description=models.TextField(blank=True,null=True,verbose_name='描叙')
#     location=models.CharField(max_length=30,blank=True,verbose_name='地点')
#     church = models.ForeignKey(Church, on_delete=models.CASCADE,related_name="userProfile",blank=True,verbose_name='教会')
#     team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="userProfile",blank=True,verbose_name='小组')

#     role = models.IntegerField(choices=ROLE_CHOICES,default=ROLE_MEMBER,verbose_name='角色')
#     date_joined=models.DateTimeField(auto_now_add=True,verbose_name='参加日期')
#     updated_on=models.DateTimeField(auto_now=True,verbose_name='更新日期')
#     creator = models.ForeignKey(userProfile, on_delete=models.CASCADE,related_name="userProfile",blank=True,verbose_name='创立者')

#     def __str__(self):
#         return self.user.username
#     class Meta:
#         verbose_name = "会友信息"
#         verbose_name_plural = "会友信息"




    
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
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
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
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
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
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "灵修评论"
        verbose_name_plural = "灵修评论"
    def __str__(self):
        return '%s' % (self.content)

    
class Course(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    speaker = models.ForeignKey('Speaker', on_delete=models.CASCADE)
    title = models.CharField(u'标题', max_length=32)
    image = models.ImageField(u'图片', upload_to='images', null=True, blank=True)
    description = models.CharField(u'描述', max_length=255)
    content = models.TextField(null=True, blank=True)
    video = models.FileField(u'视频', storage=PrivateMediaStorage(), null=True, blank=True) 
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"
    def __str__(self):
        return '%s' % (self.title)
    




