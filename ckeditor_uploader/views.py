from __future__ import absolute_import, unicode_literals

import inspect
import os
import warnings
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ckeditor_uploader import utils
from ckeditor_uploader.backends import registry
from ckeditor_uploader.forms import SearchForm
from ckeditor_uploader.utils import storage
from church.alioss_storage_backends_v3 import AliyunMediaStorage


from .utils import is_valid_image_extension
import logging
lg = logging.getLogger('church.all')





def get_upload_filename(upload_name, request):
    user_path = storage._get_user_path(request.user)

    # Generate date based path to put uploaded file.
    # If CKEDITOR_RESTRICT_BY_DATE is True upload file to date specific path.
    if getattr(settings, 'CKEDITOR_RESTRICT_BY_DATE', True):
        date_path = datetime.now().strftime('%Y/%m/%d')
    else:
        date_path = ''

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(
        settings.CKEDITOR_UPLOAD_PATH, user_path, date_path
    )

    lg.info('(%s,%s,%s)' % (settings.CKEDITOR_UPLOAD_PATH, user_path, date_path))

    if (getattr(settings, 'CKEDITOR_UPLOAD_SLUGIFY_FILENAME', True) and
            not hasattr(settings, 'CKEDITOR_FILENAME_GENERATOR')):
        upload_name = utils.slugify_filename(upload_name)

    if hasattr(settings, 'CKEDITOR_FILENAME_GENERATOR'):
        generator = import_string(settings.CKEDITOR_FILENAME_GENERATOR)
        # Does the generator accept a request argument?
        try:
            inspect.getcallargs(generator, upload_name, request)
        except TypeError:
            # Does the generator accept only an upload_name argument?
            try:
                inspect.getcallargs(generator, upload_name)
            except TypeError:
                warnings.warn(
                    "Update %s() to accept the arguments `filename, request`."
                    % settings.CKEDITOR_FILENAME_GENERATOR
                )
            else:
                warnings.warn(
                    "Update %s() to accept a second `request` argument."
                    % settings.CKEDITOR_FILENAME_GENERATOR,
                    PendingDeprecationWarning
                )
                upload_name = generator(upload_name)
        else:
            upload_name = generator(upload_name, request)

    return storage.get_available_name(
        os.path.join(upload_path, upload_name)
    )


class ImageUploadView(generic.View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        """
        Uploads a file and send back its URL to CKEditor.
        """
        uploaded_file = request.FILES['upload']

        backend = registry.get_backend()

        ck_func_num = request.GET.get('CKEditorFuncNum')
        if ck_func_num:
            ck_func_num = escape(ck_func_num)

        filewrapper = backend(storage, uploaded_file)
        allow_nonimages = getattr(settings, 'CKEDITOR_ALLOW_NONIMAGE_FILES', True)
        # Throws an error when an non-image file are uploaded.
        if not filewrapper.is_image and not allow_nonimages:
            return HttpResponse("""
                <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({0}, '', 'Invalid file type.');
                </script>""".format(ck_func_num))

        filepath = get_upload_filename(uploaded_file.name, request)
        lg.info('save filepath:%s' % filepath)
        saved_path = filewrapper.save_as(filepath)

        url = utils.get_media_url(saved_path)

        if ck_func_num:
            # Respond with Javascript sending ckeditor upload url.
            return HttpResponse("""
            <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({0}, '{1}'); 
            </script>""".format(ck_func_num, url))
        else:
            _, filename = os.path.split(saved_path)
            retdata = {'url': url, 'uploaded': '1',
                       'fileName': filename}
            return JsonResponse(retdata)


upload = csrf_exempt(ImageUploadView.as_view())




def browse(request):
    typ = request.GET["type"]
    files,dirs = storage.get_files_browse_urls(request.user,typ=typ,marker='')

    
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('q', '').lower()
            files = list(filter(lambda d: query in d[
                'visible_filename'].lower(), files))
    else:
        form = SearchForm()
    
    

    show_dirs = getattr(settings, 'CKEDITOR_BROWSE_SHOW_DIRS', False)
    # dir_list = sorted(set(os.path.dirname(f['src'])
    #                       for f in files), reverse=True)

    # Ensures there are no objects created from Thumbs.db files - ran across
    # this problem while developing on Windows
    # if os.name == 'nt':
    #     files = [f for f in files if os.path.basename(f['src']) != 'Thumbs.db']

    dirs.add(storage._get_user_path(request.user)) # dirs 是所有遍历中找到的dir, 而user_path是指定的，所以这里加上

    context = {
        'show_dirs': show_dirs,
        'dirs': list(dirs),
        'files': files,
        'form': form
    }
    lg.info(context)
    return render(request, 'ckeditor/browse.html', context)


# class Alioss_view(generic.View):
#     def list_dir(request):
#         # AliyunMediaStorage()
#         storage.listdir(browse_path)

from rest_framework.decorators import api_view, authentication_classes,permission_classes
from django.http import HttpResponse, JsonResponse
# from ImageUploadView import get_files_browse_urls
@api_view(['GET'])
def list_img(request,path=''):
    '''
    '''
    lg.info(path)
    ret = {'errCode': '0'}
    try:
        if request.method == 'GET':
            data = request.GET
            typ = data.get('type','images')
            marker = data.get('marker','')

            if path != '':
                files,dirs = storage.get_files_browse_urls(request.user,typ,path,marker)
                ret = {'errCode': '0','msg':'success','data':files}
            else:
                raise Exception('key must not null.')   
    except Exception as e:
        import traceback
        import sys
        ret = {'errCode': '1001', 'msg': 'there is an exception check logs'}
        lg.exception('There is and exceptin',exc_info=True,stack_info=True)
    finally:
        return JsonResponse(ret, safe=False)




