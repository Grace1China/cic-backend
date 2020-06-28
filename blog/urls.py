from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache

from . import views
from .view_app_LordDay import column_content_Lord_Day
from .view_app_home import theApp_home
from .vpage import vpage


urlpatterns = [
    path('sermon/<int:pk>', views.index, name='index'),
    path('tuwen/<int:pk>', views.tuwen, name='tuwen'),
    path('media/<int:pk>', views.media, name='media'),
    path('ccol/<int:pk>', views.column_content_medias, name='ccol'),
    path(r'LordDay', never_cache(column_content_Lord_Day), name='LordDay'),
    path(r'AppHome', never_cache(theApp_home), name='AppHome'),
    path(r'vpage', never_cache(vpage), name='vpage'),

]