from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.urls import path

from . import views
from church.media_browse_view import browse as mediaBaseView

urlpatterns = [
    url(r'^upload/', staff_member_required(views.upload), name='ckeditor_upload'),
    url(r'^browse/', never_cache(staff_member_required(mediaBaseView)), name='ckeditor_browse'),
    path(r'alioss_list/<path:path>/', never_cache(staff_member_required(views.list_img)), name='ckeditor_list_dir'),

]
