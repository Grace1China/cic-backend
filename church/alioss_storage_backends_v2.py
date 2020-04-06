# coding=utf-8

import os

import datetime
import six
import posixpath

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from django.core.files import File
from django.utils.encoding import force_text, filepath_to_uri, force_bytes
from oss2 import Auth, Service, BucketIterator, Bucket, ObjectIterator
from oss2.exceptions import AccessDenied
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import Storage
from oss2.api import _normalize_endpoint
import traceback, sys 
from crequest.middleware import CrequestMiddleware

import logging
theLogger = logging.getLogger('church.all')
lg = logging.getLogger('church.all')


class AliyunOperationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BucketOperationMixin(object):
    def _get_bucket(self, auth):
        if self.cname:
            return Bucket(auth, self.cname, self.bucket_name, is_cname=True)
        else:
            return Bucket(auth, self.end_point, self.bucket_name)

    def _list_bucket(self, service):
        return [bucket.name for bucket in BucketIterator(service)]

    def _create_bucket(self, auth):
        bucket = self._get_bucket(auth)
        bucket.create_bucket(settings.ALI_STORAGE_BACKEND['BUCKET_ACL_TYPE'])
        return bucket

    def _check_bucket_acl(self, bucket):
        if bucket.get_bucket_acl().acl != settings.ALI_STORAGE_BACKEND['BUCKET_ACL_TYPE']:
            bucket.put_bucket_acl(settings.ALI_STORAGE_BACKEND['BUCKET_ACL_TYPE'])
        return bucket


class AliyunBaseStorage(BucketOperationMixin, Storage):
    """
    Aliyun OSS2 Storage
    """
    location = ""

    def __init__(self):
        self.access_key_id = settings.ALI_STORAGE_BACKEND['ACCESS_KEY_ID']
        self.access_key_secret = settings.ALI_STORAGE_BACKEND['ACCESS_KEY_SECRET']
        self.end_point = _normalize_endpoint(settings.ALI_STORAGE_BACKEND['END_POINT'])
        self.bucket_name = settings.ALI_STORAGE_BACKEND['BUCKET_NAME']
        self.cname = settings.ALI_STORAGE_BACKEND['ALIYUN_OSS_CNAME']

        self.auth = Auth(self.access_key_id, self.access_key_secret)
        self.service = Service(self.auth, self.end_point)

        try:
            if self.bucket_name not in self._list_bucket(self.service):
                # create bucket if not exists
                self.bucket = self._create_bucket(self.auth)
            else:
                # change bucket acl if not consists
                self.bucket = self._check_bucket_acl(self._get_bucket(self.auth))
        except AccessDenied:
            # 当启用了RAM访问策略，是不允许list和create bucket的
            self.bucket = self._get_bucket(self.auth)

    def _get_config(self, name):
        """
        Get configuration variable from environment variable
        or django setting.py
        """
        config = os.environ.get(name, getattr(settings, name, None))
        if config is not None:
            if isinstance(config, six.string_types):
                return config.strip()
            else:
                return config
        else:
            raise ImproperlyConfigured(
                "Can't find config for '%s' either in environment"
                "variable or in setting.py" % name)

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            return clean_name + '/'
        else:
            return clean_name

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../foo.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        #theLogger.info(name)
        base_path = force_text(self.location)
        base_path = base_path.rstrip('/')

        #theLogger.info(base_path)


        final_path = '%s/%s' % (base_path.rstrip('/'),name.lstrip('/')) #urljoin(base_path.rstrip('/') + "/", name)
        #theLogger.info(final_path)


        base_path_len = len(base_path)
        if (not final_path.startswith(base_path) or
                final_path[base_path_len:base_path_len + 1] not in ('', '/')):
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      name)
        return final_path.lstrip('/')

    def _get_target_name(self, name):
        name = self._normalize_name(self._clean_name(name))
        if six.PY2:
            name = name.encode('utf-8')
        return name

    def _open(self, name, mode='rb'):
        #theLogger.info(name)
        return AliyunFile(name, self, mode)

    def _save(self, name, content):
        # 为保证django行为的一致性，保存文件时，应该返回相对于`media path`的相对路径。
        
        current_request = CrequestMiddleware.get_request()
        if current_request is None:
            raise Exception('There is now requests user found')
        
        tname = self._get_target_name(name)
        tname = '%s/%s' % (current_request.user.church.code, tname)


        theLogger.info('save location:%s' % (tname))

        content.open()
        content_str = b''.join(chunk for chunk in content.chunks())
        self.bucket.put_object(tname, content_str)
        content.close()

        return self._clean_name(name)

    def get_file_header(self, name):
        name = self._get_target_name(name)
        return self.bucket.head_object(name)

    def exists(self, name):
        return self.bucket.object_exists(name)

    def size(self, name):
        file_info = self.get_file_header(name)
        return file_info.content_length

    def modified_time(self, name):
        file_info = self.get_file_header(name)
        return datetime.datetime.fromtimestamp(file_info.last_modified)

    def listdir(self, name):
        try:
            #theLogger.info(name)
            # name = self._normalize_name(self._clean_name(name))
            if name and name.startswith('/'):
                name = name[1:]
            if name and not name.endswith('/'):
                name = '%s/' % name

            files = []
            dirs = set()
            # dirs.add(name)  不能把自已加入

            #theLogger.info(name)
            #theLogger.info(self.bucket)

            
            for obj in ObjectIterator(self.bucket, prefix=name, delimiter='/' ):#/, delimiter='/'
                if obj.is_prefix():
                    dirs.add(obj.key)
                else:
                    files.append(obj.key.replace(name,'',1))
            # raise Exception('listdir')

            theLogger.info(dirs)
            theLogger.info(files)
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
        finally:
            return list(dirs), files

    def __url(self, bucket_name, key, safe='/'):
        # self.type = _determine_endpoint_type(self.netloc, self.is_cname, bucket_name)

        # safe = '/' if slash_safe is True else ''
        from oss2.compat import urlquote,urlparse
        key = urlquote(key, safe=safe)

        p = urlparse(self.end_point)


        return '{0}://{1}.{2}/{3}'.format(p.scheme, bucket_name, p.netloc, key)

    def url(self, name):
        try:
            # theLogger.info(name)

            name = self._normalize_name(self._clean_name(name))

            current_request = CrequestMiddleware.get_request()
            if current_request is None or current_request.user is None or current_request.user.church is None or current_request.user.church.code == '':
                raise Exception('There is now requests user found or church code is not setting for user')

            theLogger.info(name)

            # name = filepath_to_uri(name) # 这段会导致二次encode
            #theLogger.info(name)
            name = '%s/%s' % (current_request.user.church.code,name)
            name = name.encode('utf8') 
            theLogger.info(name)
            # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
            # return self.bucket._make_url(self.bucket_name, name)

            # raise Exception('url %s error' % name)
            retUrl = self.__url(self.bucket_name, name,safe='/?=')#self.bucket._make_url(self.bucket_name, name,slash_safe=True) 
            # theLogger.info(retUrl)

        except:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
        finally:
            return retUrl

    def read(self, name):
        pass

    def delete(self, name):
        name = self._get_target_name(name)
        result = self.bucket.delete_object(name)
        if result.status >= 400:
            raise AliyunOperationError(result.resp)

    def create_thumbnail(self, name):
        pass

    def _get_user_path(self,user):
        user_path = ''

        # If CKEDITOR_RESTRICT_BY_USER is True upload file to user specific path.
        RESTRICT_BY_USER = getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False)
        if RESTRICT_BY_USER:
            try:
                user_prop = getattr(user, RESTRICT_BY_USER)
            except (AttributeError, TypeError):
                user_prop = getattr(user, 'get_username')

            if callable(user_prop):
                user_path = user_prop()
            else:
                user_path = user_prop

        return str(user_path)

    def get_image_files(self,user=None, path=''):
        """
        Recursively walks all dirs under upload dir and generates a list of
        full paths for each file found.
        """
        # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
        # limit images to user specific path, but not for superusers.
        STORAGE_DIRECTORIES = 0
        STORAGE_FILES = 1

        # allow browsing from anywhere if user is superuser
        # otherwise use the user path
        if user and not user.is_superuser:
            user_path = self._get_user_path(user)
        else:
            user_path = ''
        lg.info('user_path : %s' % user_path)
        lg.info('path : %s' % path)

        if path=='':
            #path 等于空时，就是第一次设置browse_path
            browse_path = '%s%s%s' % (settings.CKEDITOR_UPLOAD_PATH, user_path, path)
        else:
            #path就是从oss里面取出来的路径，不用再设置了
            browse_path = path
            
        lg.info('b u p browse_path: %s, %s, %s, %s' % (settings.CKEDITOR_UPLOAD_PATH, user_path, path, browse_path))


        try:
            storage_list = self.listdir(browse_path)
        except NotImplementedError:
            return
        except OSError:
            return
        lg.info('storage_list:')
        lg.info(storage_list)
        for filename in storage_list[STORAGE_FILES]:
            if os.path.splitext(filename)[0].endswith('_thumb') or os.path.basename(filename).startswith('.'):
                continue

            filename = '%s%s' % (browse_path, filename) if browse_path.endswith('/') else '%s/%s' % (browse_path, filename)
            yield {'name':filename,'isdir':False}
        
        for directory in storage_list[STORAGE_DIRECTORIES]:
            if directory.startswith('.'):
                continue
            else:
                yield  {'name':directory,'isdir':True}

        for directory in storage_list[STORAGE_DIRECTORIES]:
            if directory.startswith('.'):
                continue
            # directory_path = os.path.join(path, directory)
            for element in self.get_image_files(user=user, path=directory):
                yield element


    def get_files_browse_urls(self,user=None,typ=None,path=''):
        """
        Recursively walks all dirs under upload dir and generates a list of
        thumbnail and full image URL's for each file found.
        """
        from  ckeditor_uploader import utils 
        from ..utils import is_valid_image_extension
        lg.info(typ)
        files = []
        dirs = set()
        for el in self.get_image_files(user=user,path=path):
            if isinstance(el,dict) and el['isdir'] ==True:
                dirs.add(el['name'])
                continue
            filename = el['name']
            src = utils.get_media_url(filename)
            if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
                if is_valid_image_extension(src):
                    thumb = utils.get_media_url(utils.get_thumb_filename(filename))
                else:
                    thumb = utils.get_icon_filename(filename)
                visible_filename = os.path.split(filename)[1]
                if len(visible_filename) > 20:
                    visible_filename = visible_filename[0:19] + '...'
            else:
                thumb = src
                visible_filename = os.path.split(filename)[1]
            if ((typ == 'images' and is_valid_image_extension(src)) or (('.%s' % typ) == os.path.splitext(src.lower())[1])):
                # lg.info(context)
                files.append({
                    'thumb': thumb,
                    'src': src,
                    'is_image': is_valid_image_extension(src),
                    'visible_filename': visible_filename,
                })
            
        lg.info('last dirs:')
        lg.info(dirs)
        return (files,dirs)

from django.utils.deconstruct import deconstructible
@deconstructible
class AliyunMediaStorage(AliyunBaseStorage):
    
    location = settings.MEDIA_ROOT
    def get_files_browse_urls(self,user=None,typ=None,path=''):
        return super().get_files_browse_urls(user=user,typ=typ,path=path)
    def get_image_files(self,user=None, path=''):
        return super().get_image_files(user=user,path=path)
    
    # def getLocation():
    #     current_request = CrequestMiddleware.get_request()
    #     if current_request is None:
    #         raise Exception('There is now requests user found')
    #     return current_request.user.church.code
        



@deconstructible
class AliyunStaticStorage(AliyunBaseStorage):
    location = settings.STATIC_URL

@deconstructible
class AliyunFile(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        #theLogger.info('self._storage.location')
        #theLogger.info(self._storage.location)
        # self._name = name[len(self._storage.location):]
        self._name= self._storage.location[1:]+ name
        theLogger.info('AliyunFile self._name')
        theLogger.info(self._name)
        self._mode = mode
        self.file = six.BytesIO()
        self._is_dirty = False
        self._is_read = False
        super(AliyunFile, self).__init__(self.file, self._name)

    def read(self, num_bytes=None):
        if not self._is_read:
            content = self._storage.bucket.get_object(self._name)
            self.file = six.BytesIO(content.read())
            self._is_read = True

        if num_bytes is None:
            data = self.file.read()
        else:
            data = self.file.read(num_bytes)

        if 'b' in self._mode:
            return data
        else:
            return force_text(data)

    def write(self, content):
        if 'w' not in self._mode:
            raise AliyunOperationError("Operation write is not allowed.")

        self.file.write(force_bytes(content))
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            self.file.seek(0)
            self._storage._save(self._name, self.file)
        self.file.close()
