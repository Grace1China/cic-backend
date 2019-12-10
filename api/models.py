from django.db import models
from django.contrib.auth.models import User
from churchs.models import Church

# Create your models here.

class userProfile(models.Model):
    ROLE_MEMBER = 1
    ROLE_GROUPLEAD = 2
    ROLE_CHURCHLEAD = 3


    ROLE_CHOICES = (
        (ROLE_MEMBER ,'会员'),
        (ROLE_GROUPLEAD , '组长'),
        (ROLE_CHURCHLEAD ,'教会管理员')
    )
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    description=models.TextField(blank=True,null=True)
    location=models.CharField(max_length=30,blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE,related_name="profile",blank=True)
    role = models.IntegerField(
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER
    )
    date_joined=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name = "会友"
        verbose_name_plural = "会友"
