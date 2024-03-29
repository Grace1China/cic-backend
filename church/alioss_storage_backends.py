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

import logging
theLogger = logging.getLogger('church.all')


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
        theLogger.info(name)
        base_path = force_text(self.location)
        base_path = base_path.rstrip('/')

        theLogger.info(base_path)


        final_path = '%s/%s' % (base_path.rstrip('/'),name.lstrip('/')) #urljoin(base_path.rstrip('/') + "/", name)
        theLogger.info(final_path)


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
        theLogger.info(name)
        return AliyunFile(name, self, mode)

    def _save(self, name, content):
        # 为保证django行为的一致性，保存文件时，应该返回相对于`media path`的相对路径。
        target_name = self._get_target_name(name)

        content.open()
        content_str = b''.join(chunk for chunk in content.chunks())
        self.bucket.put_object(target_name, content_str)
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
            theLogger.info(name)
            # name = self._normalize_name(self._clean_name(name))
            if name and name.endswith('/'):
                name = name[:-1]

            files = []
            dirs = set()

            theLogger.info(name)
            theLogger.info(self.bucket)


            for obj in ObjectIterator(self.bucket, prefix=name ):#/, delimiter='/'
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

    def url(self, name):
        try:
            # theLogger.info(name)

            name = self._normalize_name(self._clean_name(name))
            # name = filepath_to_uri(name) # 这段会导致二次encode
            theLogger.info(name)
            name = name.encode('utf8') 
            # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
            # return self.bucket._make_url(self.bucket_name, name)

            # raise Exception('url %s error' % name)

        except:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
        finally:
            return self.bucket._make_url(self.bucket_name, name) 

    def read(self, name):
        pass

    def delete(self, name):
        name = self._get_target_name(name)
        result = self.bucket.delete_object(name)
        if result.status >= 400:
            raise AliyunOperationError(result.resp)


class AliyunMediaStorage(AliyunBaseStorage):
    location = settings.MEDIA_URL


class AliyunStaticStorage(AliyunBaseStorage):
    location = settings.STATIC_URL


class AliyunFile(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        theLogger.info('self._storage.location')
        theLogger.info(self._storage.location)
        # self._name = name[len(self._storage.location):]
        self._name= self._storage.location[1:]+ name
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
