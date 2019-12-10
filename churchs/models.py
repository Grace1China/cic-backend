from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User

# Create your models here.

class Venue(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.TimeField()
    address = models.CharField(max_length=255)
    addressUrl =  models.CharField(max_length=255)
    class Meta:
        verbose_name = "场地"
        verbose_name_plural = "场地"
    


class Church(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2
    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,blank=False)
    code = models.CharField(max_length=32,unique=True,blank=False,default='086-010-0001')
    description = models.CharField(max_length=255)
    address = models.CharField(max_length=32)
    promot_cover =  models.ImageField(u'海报封面', storage=PrivateMediaStorage(), null=True, blank=True)
    promot_video =  models.FileField(u'海报短片', storage=PrivateMediaStorage(), null=True, blank=True)
    vunue = models.ManyToManyField(to="Venue",default=None)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_INITED
    )
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "教会"
        verbose_name_plural = "教会"
     

class SermonSeries(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    title = models.CharField(u'标题', max_length=32, default='')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True)
    STATUS_OPEN = 1
    STATUS_CLOSE = 2

    STATUS_CHOICES = (
        (STATUS_OPEN, '在线'),
        (STATUS_CLOSE, '下线')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_CLOSE
    )

    class Meta:
        verbose_name = "讲道系列"
        verbose_name_plural = "讲道系列"
    

class Sermon(models.Model):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2

    STATUS_CHOICES = (
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '发布')
    )
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    title = models.CharField(u'标题', max_length=32, default='')
    date = models.DateField()
    description = models.TextField(u'敬拜', null=True, blank=True)
    pdf = models.FileField(storage=PrivateMediaStorage(),null=True, blank=True)
    speaker = models.ForeignKey("church.Speaker",on_delete=models.CASCADE,default=None)
    scripture = models.CharField(max_length=100, default='')
    series = models.ForeignKey(SermonSeries, on_delete=models.CASCADE,null=True,default=None)
    cover = models.ImageField(u'图片', storage=PrivateMediaStorage(), null=True, blank=True)
    worshipvideo = models.FileField(u'敬拜', storage=PrivateMediaStorage(), null=True, blank=True)
    mcvideo = models.FileField(u'主持', storage=PrivateMediaStorage(), null=True, blank=True)
    sermonvideo = models.FileField(u'讲道', storage=PrivateMediaStorage(), null=True, blank=True)
    givingvideo = models.FileField(u'奉献', storage=PrivateMediaStorage(), null=True, blank=True)
    # worshiptext = models.TextField(u'敬拜', null=True, blank=True)
    # content = RichTextUploadingField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(null=True, blank=True,editable=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    class Meta:
        verbose_name = "主日信息"
        verbose_name_plural = "主日信息"


class WeeklyReport(models.Model):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2

    STATUS_CHOICES = (
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '发布')
    )
    church = models.ForeignKey(Church, on_delete=models.CASCADE,default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    title = models.CharField(u'标题', max_length=32, default='')
    image = models.ImageField(u'图片', storage=PrivateMediaStorage(), null=True, blank=True)
    content = RichTextUploadingField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pub_time = models.DateTimeField(auto_now_add=True,null=True, blank=True,editable=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    class Meta:
        verbose_name = "周报"
        verbose_name_plural = "周报"

class Member(models.Model):
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=16)
    password = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "会友"
        verbose_name_plural = "会友"


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

    
class Donation(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    Member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=10, max_digits=12)
    pay_type = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pay_time = models.DateTimeField(null=True)
    class Meta:
        verbose_name = "奉献"
        verbose_name_plural = "奉献"

