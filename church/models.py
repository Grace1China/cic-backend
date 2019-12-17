from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from users.models import CustomUser

class Church(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2
    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32,blank=False,verbose_name='名称')
    code = models.CharField(max_length=32,unique=True,blank=False,default='086-010-0001',verbose_name='代码')
    description = models.CharField(max_length=255,verbose_name='描叙')
    address = models.CharField(max_length=32,verbose_name='地址')
    promot_cover =  models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='海报封面')
    promot_video =  models.FileField(storage=PrivateMediaStorage(), null=True, blank=True,verbose_name='海报短片')
    vunue = models.ManyToManyField(to="churchs.Venue",default=None, null=True, blank=True,verbose_name='场地')
    status = models.IntegerField(choices=STATUS_CHOICES,default=STATUS_INITED,verbose_name='状态')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name='更新时间')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name='creatoruser',verbose_name='创建者')
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True,related_name='manageruser',verbose_name='管理者')

    class Meta:
        verbose_name = "教会"
        verbose_name_plural = "教会"

    def __str__(self):
        return '%s' % (self.name)


    
