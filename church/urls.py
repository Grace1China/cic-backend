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
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import url, include
from . import view
from api import urls as apiusrls
# from api
import logging

schema_view = get_swagger_view(title='Church API')

urlpatterns = [
    path('hello', view.hello),
    path('admin/', admin.site.urls),
    re_path('swagger/', schema_view),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # re_path(r'^api/auth/', include('rest_auth.urls')),
    # re_path(r'^api/auth/registration/', include('rest_auth.registration.urls')),
    # re_path(r'^api/accounts/', include('allauth.urls')),
    # re_path(r'^admin/ckeditor/', include('ckeditor_uploader.urls')),
    #path to djoser end points
    re_path('rapi/auth/', include('djoser.urls')),
    re_path('rapi/auth/', include('djoser.urls.jwt')),
    re_path(r'^rapi/',include('api.urls'))
]
# print(apiusrls.urlpatterns)
# logging.debug(apiusrls)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
