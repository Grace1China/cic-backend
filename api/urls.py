from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import SermonDetailView,UserProfileViewSet,EweeklyView
user_create = UserProfileViewSet.as_view({
    'post': 'create'
})
user_list = UserProfileViewSet.as_view({
    'get': 'list'
})

urlpatterns = [
    path("user_create",csrf_exempt(user_create),name="user_create"),
    path("user_list",user_list,name="user_list"),
    # path("userProfile/<int:pk>",userProfileDetailView.as_view(),name="userProfile"),
    path("sermon/<int:pk>",SermonDetailView.as_view(),name="sermon"),
    path("eweekly/<int:pk>",EweeklyView.as_view(),name="eweekly")

]
