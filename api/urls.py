from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from .views import UserProfileListCreateView, userProfileDetailView,SermonDetailView

urlpatterns = [
    #gets all user profiles and create a new profile
    path("all-profiles",UserProfileListCreateView.as_view(),name="all-profiles"),
   # retrieves profile details of the currently logged in user
    path("profile/<int:pk>",userProfileDetailView.as_view(),name="profile"),
    path("sermon/<int:pk>",SermonDetailView.as_view(),name="sermon")
]
