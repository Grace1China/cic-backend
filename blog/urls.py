from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache

from . import views
from .view_app_LordDay import column_content_Lord_Day

urlpatterns = [
    path('sermon/<int:pk>', views.index, name='index'),
    path('tuwen/<int:pk>', views.tuwen, name='tuwen'),
    path('media/<int:pk>', views.media, name='media'),
    path('ccol/<int:pk>', views.column_content_medias, name='ccol'),
    path(r'LordDay', never_cache(column_content_Lord_Day), name='LordDay'),#this is for /根目录没有匹配的情况


]