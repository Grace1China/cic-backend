from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import SermonDetailView,CustomUserViewSet,ChurchViewSet,EweeklyViewSet,SermonViewSet
from .alioss_directup_views import AliOssSignature, AliOssCallBack
from rest_framework import permissions

from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib.auth.models import Group

user_create = CustomUserViewSet.as_view({
    'post': 'register'
})
user_list = CustomUserViewSet.as_view({
    'get': 'list'
})
user_church = ChurchViewSet.as_view({
    'get':'GetUserChurch'
})
l3_eweekly = EweeklyViewSet.as_view({
    'get':'GetL3Eweekly'
})
church_eweekly = EweeklyViewSet.as_view({
    'get':'GetChurchEweekly'
})

v2_church_eweekly = EweeklyViewSet.as_view({
    'get':'GetChurchEweekly_v2'
})

l3_lorddayinfo = SermonViewSet.as_view({'get':'GetDefaultLordsDayInfo'})
church_lorddayinfo = SermonViewSet.as_view({'get':'GetCurrentLordsDayInfo'})

urlpatterns = [
    path("user_create",csrf_exempt(user_create),name="user_create"),
    path("user_list",user_list,name="user_list"),
    # path("userProfile/<int:pk>",userProfileDetailView.as_view(),name="userProfile"),
    path("sermon/0",church_lorddayinfo,name="sermon"),
    
    path("lorddayinfo/l3",l3_lorddayinfo,name="l3_lorddayinfo"),
    path("lorddayinfo",church_lorddayinfo,name="lorddayinfo"),
    path("eweekly/<int:pk>",church_eweekly,name="church_eweekly"),
    path("eweekly",v2_church_eweekly,name="church_eweekly"),

    path("eweekly/l3",l3_eweekly,name="l3_eweekly"),
    path("getmychurch",user_church,name="mychurch"),

    path("alioss_directup_signature",AliOssSignature.as_view(),name="alioss_directup_signature"),
    path("alioss_directup_callback",AliOssCallBack.as_view(),name="alioss_directup_callback")


]
