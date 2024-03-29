from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# from church.models import Church
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True,verbose_name='电子邮件')
    username = models.CharField(max_length=30,db_index=True,blank=True,verbose_name='用户呢称')
    is_staff = models.BooleanField(default=False,verbose_name='是否管理者')
    is_active = models.BooleanField(default=True,verbose_name='是否激活')
    
    date_joined = models.DateTimeField(default=timezone.now,verbose_name='参加时间')
    creator = models.ForeignKey('CustomUser', on_delete=models.CASCADE,blank=True,null=True,verbose_name='创建者')
    church = models.ForeignKey('church.Church', on_delete=models.CASCADE,blank=True,null=True,verbose_name='教会')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # courses = models.ManyToManyField("church.Course", through='payment.Users_Courses', related_name="owners", null=True, blank=True)
    
    def groups_list(self):
        return ', '.join([a.name for a in self.groups.all()])
    groups_list.short_description = '所属组'
    @property
    def first_group(self):
        self.groups.all().first() 

    @property
    def get_church_path(self):
        return self.church.code


    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"


class VerifyCode(models.Model):
    email = models.EmailField(unique=True,db_index=True,verbose_name='电子邮件')
    verify_code = models.CharField(max_length=6,verbose_name='验证码')
