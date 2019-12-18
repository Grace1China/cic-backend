from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import SermonDetailView,CustomUserViewSet,EweeklyView,ChurchViewSet
user_create = CustomUserViewSet.as_view({
    'post': 'register'
})
user_list = CustomUserViewSet.as_view({
    'get': 'list'
})
user_church = ChurchViewSet.as_view({
    'get':'GetUserChurch'
})

urlpatterns = [
    path("user_create",csrf_exempt(user_create),name="user_create"),
    path("user_list",user_list,name="user_list"),
    # path("userProfile/<int:pk>",userProfileDetailView.as_view(),name="userProfile"),
    path("sermon/<int:pk>",SermonDetailView.as_view(),name="sermon"),
    path("eweekly/<int:pk>",EweeklyView.as_view(),name="eweekly"),
    path("getmychurch",user_church,name="mychurch")


]
