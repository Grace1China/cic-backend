from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from users.models import CustomUser
from django.core.validators import *
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# from filer.fields.image import FilerImageField
# from filer.fields.file import FilerFileField
from church.alioss_storage_backends_v2 import AliyunMediaStorage,AliyunStaticStorage
from church.confs.base import get_ALIOSS_DESTINATIONS

class Church(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2
    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,blank=False,verbose_name='名称')
    code = models.CharField(max_length=32,unique=True,blank=False,default='086-010-0001',verbose_name='代码',help_text='只能含有字母，数字, _和-, 不要超过 254个字符',validators=[validate_slug])
    description = models.CharField(max_length=255,verbose_name='描叙')
    address = models.CharField(max_length=32,verbose_name='地址')
    # promot_cover =  models.ImageField(storage=AliyunMediaStorage(), null=True, blank=True,verbose_name='海报封面')
    promot_cover = models.CharField(max_length=400,null=True, blank=True,verbose_name='海报封面')
    giving_qrcode =  models.CharField(max_length=400,null=True, blank=True,verbose_name='奉献二维码')
    #FilerImageField(on_delete=models.CASCADE,null=True, blank=True,verbose_name='海报封面',related_name="logo_company")#models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='海报封面')
    promot_video =  models.CharField(max_length=400,null=True, blank=True,verbose_name='海报短片')
    venue = models.ManyToManyField(to="churchs.Venue",default=None,  blank=True,verbose_name='场地')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_INITED,verbose_name='状态')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name='更新时间')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,default=None,related_name='creatoruser',verbose_name='创建者')
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,default=None,related_name='manageruser',verbose_name='管理者')

    class Meta:
        verbose_name = "教会基本信息"
        verbose_name_plural = "教会基本信息"

    def __str__(self):
        return '%s' % (self.name)


    @property
    def fullpath_giving_qrcode(self):
        retval = 'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ = 'images')['redirecturl'],self.giving_qrcode)
        return retval 

    @property
    def fullpath_promot_cover(self):
        retval = 'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ = 'images')['redirecturl'],self.promot_cover)
        return retval 
    
    @property
    def fullpath_promot_video(self):
        retval = 'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ = 'videos')['redirecturl'],self.promot_video)
        return retval 

        
class Course(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会或平台，默认是用户所在的组织')
    teacher = models.ForeignKey('churchs.Speaker',null=True, blank=True,on_delete=models.CASCADE,verbose_name='讲员')
    iap_charge = models.ForeignKey("payment.IAPCharge", on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='内购价格')
    title = models.CharField(max_length=500,verbose_name='标题')
    # image = models.ImageField(u'图片', upload_to='images', null=True, blank=True)
    description = models.TextField(max_length=255, blank=True,verbose_name='描叙')
    content = RichTextField(null=True, blank=True,verbose_name='内容')
    price = models.DecimalField(default=0,max_digits=9, decimal_places=2,verbose_name='人民币价格')
    price_usd = models.DecimalField(default=0,max_digits=9, decimal_places=2,verbose_name='美元价格')
    # s3video = models.FileField(u'视频', storage=PrivateMediaStorage(), null=True, blank=True) 

    users = models.ManyToManyField("users.CustomUser", through='payment.Users_Courses', related_name="courses", blank=True)
    sales_num = models.IntegerField(default=0)
    
    import churchs.models as churchs_models
    medias = GenericRelation(churchs_models.Media, related_query_name='Course',verbose_name='视听媒体')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name='更新时间')
    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"
    def __str__(self):
        return '%s' % (self.title)

