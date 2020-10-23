"""church URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import url, include
from . import view
from . import media_browse_view
from api import urls as apiusrls
from  rest_framework import routers

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache

# from api
import logging
from django.conf import settings
from rest_framework import permissions

# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
from django.conf.urls.static import static

router = routers.DefaultRouter()

# schema_view = get_schema_view(
#    openapi.Info(
#       title="Church API",
#       default_version='v1',
#       description="No",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="danielqin@bicf.org"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )


urlpatterns = [
    url('^admin/', admin.site.urls),

    # url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/ckeditor/', include('ckeditor_uploader.urls')),
    #path to djoser end points
    # url('rapi/auth/', include('djoser.urls')),
    url('rapi/auth/', include('djoser.urls.jwt')),
    url(r'^rapi/',include('api.urls')),
    url(r'^admin/s3direct/', include('s3direct.urls')),
    
    path('rapi/', include('payment.urls')),

    path('blog/', include('blog.urls')),
    # url(r'^filer/', include('filer.urls')),
    # url(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),

    url(r'^media_browse/', never_cache(staff_member_required(media_browse_view.browse)),name="media_browse"),
    url(r'^com_builder/', never_cache(staff_member_required(media_browse_view.com_builder)),name="com_builder"),
    url(r'^admin/media_browse/', never_cache(staff_member_required(media_browse_view.browse)),name="media_browse"),
    path(r'alioss_list/<path:path>', never_cache(staff_member_required(media_browse_view.list_img)), name='media_list_dir'),
    path(r'alioss_list/', never_cache(staff_member_required(media_browse_view.list_img)), name='media_list_dir'),#this is for /根目录没有匹配的情况



]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)