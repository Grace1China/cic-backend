from rest_framework import serializers
from users.models import CustomUser
from church.models import Church
from churchs.models import Venue, Sermon, Media, Speaker
from django.contrib.auth.hashers import make_password
from django.conf import settings
import boto3


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

class ChurchSerializer4API(serializers.ModelSerializer):
    venue = venueSerializer4API(required=False,many=True)

    class Meta:
        model = Church
        fields = ['id','name','code','venue','description','promot_cover','promot_video']

class SpeakerSerializer4API(serializers.ModelSerializer):

    class Meta:
        model = Speaker
        fields = '__all__'


# media:
# ----------------------
# owner
# kind 
# title
# video
# video_status 
# SHD_URL
# HD_URL
# SD_URL
# audio
# image
# pdf
# content
class MediaSerializer4API(serializers.ModelSerializer):
    image_presigned_url = serializers.SerializerMethodField()
    pdf_presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ['owner','kind','title','video','video_status','SHD_URL','HD_URL','SD_URL','audio','image','image_presigned_url','pdf_presigned_url','pdf','content']
    def get_image_presigned_url(self, obj):
        url = obj.image
        if url == None or len(url) == 0:
            return obj.image
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
        
    def get_pdf_presigned_url(self, obj):
        url = obj.image
        if url == None or len(url) == 0:
            return obj.image
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


class SermonSerializer4API(serializers.ModelSerializer):
    medias = MediaSerializer4API(many=True, read_only=True)
    church = ChurchSerializer4API(read_only=True)
    speaker = SpeakerSerializer4API(read_only=True)


    class Meta:
        model = Sermon
        fields = ['id','church','user','title','speaker','scripture','series','medias','create_time','update_time','pub_time','status']


# sermon:
# -------------------
# id 
# church
# user
# title
# speaker
# scripture
# series
# create_time
# update_time
# pub_time
# status


        