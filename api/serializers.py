from rest_framework import serializers
from users.models import CustomUser
from church.models import Church
from churchs.models import Venue, Sermon, Media, Speaker, SermonSeries
from payment.serializers import IAPChargeSerializer
from django.contrib.auth.hashers import make_password
from django.conf import settings
import boto3
from django.db import models
from rest_framework import serializers
from .import models

class CustomUser4Info(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        exclude = ('password',)

class CustomUserSerializer(serializers.ModelSerializer):
    user=serializers.StringRelatedField(read_only=True)
    # church=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=CustomUser
        fields='__all__'
        # extra_kwargs = {'church_code': True}

class CustomUser4APISerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    church_code = serializers.CharField(source='church.code')
    # email = serializers.EmailField(unique=True,verbose_name='电子邮件')
    # username = models.CharField(max_length=30,db_index=True,blank=True,verbose_name='用户呢称')
    # is_staff = models.BooleanField(default=False,verbose_name='是否管理者')
    # is_active = models.BooleanField(default=True,verbose_name='是否激活')
    
    # date_joined = models.DateTimeField(default=timezone.now,verbose_name='参加时间')
    # creator = serializers.ForeignKey('CustomUser', on_delete=models.CASCADE,blank=True,null=True,verbose_name='创建者')

    # church=serializers.StringRelatedField(read_only=True)
    
    # 已购买课程
    # courses = CourseSerializer(many=True, read_only=True)
    
    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)
    class Meta:
        model=CustomUser
        fields=['id','email','username','password','church_code']
        # extra_kwargs = {'church_code': True}

class venueSerializer4API(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'



class ChurchSerializer4Sermon(serializers.ModelSerializer):
    venue = venueSerializer4API(required=False,many=True)

    class Meta:
        model = Church
        fields=['id','name','code','description','address','status','venue']


class ChurchSerializer4API(serializers.ModelSerializer):
    venue = venueSerializer4API(required=False,many=True)

    class Meta:
        model = Church
        fields =  '__all__'

class SpeakerSerializer4API(serializers.ModelSerializer):

    class Meta:
        model = Speaker
        fields = '__all__'

class SermonSeriesSerializer4API(serializers.ModelSerializer):

    class Meta:
        model = SermonSeries
        fields = '__all__'

class MediaSerializer4ListAPI(serializers.ModelSerializer):
    # image_presigned_url = serializers.SerializerMethodField()
    # pdf_presigned_url = serializers.SerializerMethodField()
    video = serializers.CharField(source='dist_list_video', max_length=400)
    video_status = serializers.IntegerField(source='dist_video_status')
    SHD_URL = serializers.CharField(source='dist_list_SHD_URL', max_length=400)
    HD_URL = serializers.CharField(source='dist_list_HD_URL', max_length=400)
    SD_URL = serializers.CharField(source='dist_list_SD_URL', max_length=400)
    audio = serializers.CharField(source='dist_list_audio', max_length=400)
    image = serializers.CharField(source='dist_list_image', max_length=400)
    pdf = serializers.CharField(source='dist_list_pdf', max_length=400)


    class Meta:
        model = Media
        fields = ['video','video_status','SHD_URL','HD_URL','SD_URL','audio','image','pdf']
    

class MediaSerializer4API(serializers.ModelSerializer):
    # image_presigned_url = serializers.SerializerMethodField()
    # pdf_presigned_url = serializers.SerializerMethodField()
    video = serializers.CharField(source='dist_video', max_length=400)
    video_status = serializers.IntegerField(source='dist_video_status')
    SHD_URL = serializers.CharField(source='dist_SHD_URL', max_length=400)
    HD_URL = serializers.CharField(source='dist_HD_URL', max_length=400)
    SD_URL = serializers.CharField(source='dist_SD_URL', max_length=400)
    audio = serializers.CharField(source='dist_audio', max_length=400)
    image = serializers.CharField(source='dist_image', max_length=400)
    pdf = serializers.CharField(source='dist_pdf', max_length=400)


    class Meta:
        model = Media
        fields = ['kind','title','video','video_status','SHD_URL','HD_URL','SD_URL','audio','image','pdf','content']
    


class SermonSerializer4API(serializers.ModelSerializer):
    medias = MediaSerializer4API(many=True, read_only=True)
    church = ChurchSerializer4Sermon(read_only=True)
    speaker = SpeakerSerializer4API(read_only=True)
    series = SermonSeriesSerializer4API(read_only=True)


    class Meta:
        model = Sermon
        fields = ['id','church','user','title','pub_time','status','speaker','scripture','series','medias','create_time','update_time']

class SermonListSerializer4API(serializers.ModelSerializer):
    speaker = SpeakerSerializer4API(read_only=True)
    medias = MediaSerializer4ListAPI(many=True, read_only=True)
    # church = ChurchSerializer4Sermon(read_only=True)
    # series = SermonSeriesSerializer4API(read_only=True)
    class Meta:
        model = Sermon
        fields = ['id','user','title','cover','pub_time','status','speaker','medias','scripture','create_time','update_time']


class CourseSerializer4APIPOST(serializers.ModelSerializer):
    pagesize = serializers.IntegerField(default=10)
    page = serializers.IntegerField(default=1)
    keyword = serializers.CharField(default=None)
    orderby = serializers.CharField(default=None)

    class Meta:
        model = models.Course
        fields = ['pagesize','page','keyword','orderby']

    
class CourseSerializer4API(serializers.ModelSerializer):
    medias = MediaSerializer4API(many=True, read_only=True)
    church = ChurchSerializer4API(read_only=True)
    speaker = SpeakerSerializer4API(source='teacher',read_only=True)
    # series = SermonSeriesSerializer4API(read_only=True)
    # speaker = serializers.PrimaryKeyRelatedField(source='teacher', queryset=Speaker.objects.all())
    iap_charge = IAPChargeSerializer(read_only=True)
    
    # users = CustomUser4APISerializer(many=True)
    # users = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    is_buy = serializers.BooleanField(required=False,default=None)
    sales_num = serializers.IntegerField(default=0)
    
    class Meta:
        model = models.Course
        fields = ['id','church','speaker','title','description','content','price','price_usd','iap_charge','medias','sales_num','is_buy','create_time','update_time']

