from rest_framework import serializers
from users.models import CustomUser
from church.models import Church
from churchs.models import Venue 
from django.contrib.auth.hashers import make_password

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
        
        