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
# from rest_framework_swagger.views import get_swagger_view
# from api.schema_view import schema_view
from django.conf.urls import url, include
from . import view
from api import urls as apiusrls
# from api
import logging
from django.conf import settings
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# schema_view = get_swagger_view(title='Church API')

schema_view = get_schema_view(
   openapi.Info(
      title="Church API",
      default_version='v1',
      description="No",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="danielqin@bicf.org"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('hello', view.hello),
    re_path('^admin/', admin.site.urls),
    # path('admindev/', admin.site.urls),

    # url(^'swagger/', schema_view),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^admin/ckeditor/', include('ckeditor_uploader.urls')),
    # re_path(r'^admindev/ckeditor/', include('ckeditor_uploader.urls')),


    # re_path(r'^api/auth/', include('rest_auth.urls')),
    # re_path(r'^api/auth/registration/', include('rest_auth.registration.urls')),
    # re_path(r'^api/accounts/', include('allauth.urls')),
    #path to djoser end points
    re_path('rapi/auth/', include('djoser.urls')),
    re_path('rapi/auth/', include('djoser.urls.jwt')),
    re_path(r'^rapi/',include('api.urls')),
    # url(r'^admin/',include(('photos.urls','photos'), namespace='photos')),
    url(r'^admin/s3direct/', include('s3direct.urls')),

]
# print(apiusrls.urlpatterns)
# logging.debug(apiusrls)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
