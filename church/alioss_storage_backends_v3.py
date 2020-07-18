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
from churchs.models import MediaFile,WeeklyReport
from django.core.paginator import Paginator
from churchs.models import Media
import urllib.request
from django.db.models import Q

import qrcode
from io import BytesIO
import base64
# def make_qrcode(text):
#     qr = qrcode.QRCode(
#         version=5,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=8,
#         border=4
#     )
#     qr.add_data(text)
#     qr.make(fit=True)
    
#     img = qr.make_image()


#     output_buffer = BytesIO()
#     img.save(output_buffer, format='png')
#     byte_data = output_buffer.getvalue()
#     base64_str = base64.b64encode(byte_data)
#     return base64_str


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

    def listdir1(self,name,marker=''):
        try:
            if name and name.startswith('/'):
                name = name[1:]
            if name and not name.endswith('/'):
                name = '%s/' % name

            files = []
            dirs = set()
            for obj in ObjectIterator(self.bucket, prefix=name, delimiter='/',marker=marker):#/, delimiter='/'
                if obj.is_prefix():
                    dirs.add(obj.key)
                else:
                    files.append(obj.key.replace(name,'',1))
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
        finally:
            return list(dirs), files


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
            raise e
        finally:
            return list(dirs), files

    # def __url(self, bucket_name, key, safe='/'):
    #     # self.type = _determine_endpoint_type(self.netloc, self.is_cname, bucket_name)

    #     # safe = '/' if slash_safe is True else ''
    #     from oss2.compat import urlquote,urlparse
    #     key = urlquote(key, safe=safe)

    #     p = urlparse(self.end_point)


    #     return '{0}://{1}.{2}/{3}'.format(p.scheme, bucket_name, p.netloc, key)

    # def url(self, name):
    #     try:
    #         # theLogger.info(name)
    #         name = self._normalize_name(self._clean_name(name))
    #         name = '%s/%s' % (self._get_user_path(None),name)
    #         name = name.encode('utf8')
    #         theLogger.info(name)
    #         # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
    #         retUrl = self.__url(self.bucket_name, name,safe='/?=')#self.bucket._make_url(self.bucket_name, name,slash_safe=True) 
    #     except:
    #         import traceback
    #         theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #     finally:
    #         return retUrl
    def url(self, name, addUpath = True):
        try:
            name = self._normalize_name(self._clean_name(name))
            key = '%s/%s' % (self._get_user_path(None),name) if addUpath else name #加入用户的教会目录
            key = key.encode('utf8')
            # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
            # retUrl = self.__url(self.bucket_name, name,safe='/?=')#self.bucket._make_url(self.bucket_name, name,slash_safe=True) 
            from oss2.compat import urlquote,urlparse
            key = urlquote(key, safe='/?=')
            p = urlparse(self.end_point)
            return '{0}://{1}.{2}/{3}'.format(p.scheme, bucket_name, p.netloc, key)
        except Exception as e:
            import traceback
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
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
        if user is None:
            current_request = CrequestMiddleware.get_request()
            user = current_request.user
    
        if (user is not None) and  (hasattr(user,'church')) and (user.church.code != ''):
            return user.church.code

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

        if getattr(settings, 'DEFAULT_CHURCH', '') != '':
            return getattr(settings, 'DEFAULT_CHURCH', '')

        raise Exception('not find the user resource path!')

    def del_get_image_files(self,user=None, path='',marker=''):
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
            storage_list = self.listdir1(browse_path,marker=marker)
        except NotImplementedError:
            return
        except OSError:
            return
        lg.info('storage_list:(path:%s,marker:%s)' % (browse_path,marker))
        lg.info(storage_list)
        c = 0 
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
            for element in self.get_image_files(user=user, path=directory, marker = marker):
                yield element

    def get_thumb_filename(self, file_name):
        """
        Generate thumb filename by adding _thumb to end of
        filename before . (if present)
        """
        return '%s?%s' % (file_name,'x-oss-process=style/wh124')

    def get_files_browse_urls(self,user=None,typ=None,path='',marker = ''):
        """
        Recursively walks all dirs under upload dir and generates a list of
        thumbnail and full image URL's for each file found.
        """
        from  ckeditor_uploader import utils 
        from .utils import is_valid_image_extension
        lg.info(typ)
        files = []
        dirs = set()
        c = 0 
        for el in self.get_image_files( user=user, path=path, marker=marker) :
            if isinstance(el,dict) and el['isdir'] ==True:
                dirs.add(el['name'])
                continue
            
            filename = el['name']
            src = self.media_url(filename,addUpath=False)
            if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
                if is_valid_image_extension(src):
                    thumb = self.media_url(self.get_thumb_filename(filename),addUpath=False)
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
                c = c + 1 
                if c > 18 : 
                    break
                files.append({
                    'thumb': thumb,
                    'src': src,
                    'is_image': is_valid_image_extension(src),
                    'visible_filename': visible_filename,
                })
            
        lg.info('last (files dirs):')
        lg.info((files,dirs))
        return (files,dirs)

from django.utils.deconstruct import deconstructible
@deconstructible
class AliyunMediaStorage(AliyunBaseStorage):
    
    location = '/'#settings.MEDIA_ROOT
    destination = "destination" #在父类url中使用取得redirect url getattr(self, 'out')# 获取子类的out()方法
    def get_files_browse_urls(self,user=None,typ=None,path='',marker = ''):
        self._set_bucket(dest=typ)  #根据不同的媒体 取不同的存储桶 不同的存储桶，有不同的访问url，跨国加速url和redirect url
        return super().get_files_browse_urls(user=user,typ=typ,path=path,marker = marker)

    def del_get_media_from_db(self,typ='images',key=''):
        '''
        '''
        try:
            if key == '' :
                raise Exception(' key should not be null ')
            self._set_bucket(dest=typ)  #根据不同的媒体 取不同的存储桶 不同的存储桶，有不同的访问url，跨国加速url和redirect url  同时会对self.destination进行赋值
            qrset = MediaFile.objects.filter(name=key)
            from  ckeditor_uploader import utils 
            from .utils import is_valid_image_extension
            
            key = self._normalize_name(self._clean_name(key))
            key = key.encode('utf8')
            # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
            from oss2.compat import urlquote,urlparse
            key = urlquote(key, safe='/?=')
            p = urlparse(rc.endpoint)

            media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[self.destination]['redirecturl'], key)

            thumb = self.get_thumb_filename(media_url)

            qs = MediaFile.objects.filter(name=key)
            if len(qs) != 1:
                raise Exception(' media record is not unique ')

            ro = {
                'thumb': thumb,
                'src': media_url,
                'key':key,
                'is_image': is_valid_image_extension(qs[0].origin_name),
                'typ':typ,
                'visible_filename': qs[0].origin_name,
            }
                
            return files
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e


    def get_files_from_db(self,request=None,typ=None,series='',page=1,dkey='',skey=''):
        '''
        从数据库中，查找媒体记录
        '''
        try:
            if request == None:
                raise Exception(' no request is pass in.')
            user = request.user
            self._set_bucket(dest=typ)  #根据不同的媒体 取不同的存储桶 不同的存储桶，有不同的访问url，跨国加速url和redirect url  同时会对self.destination进行赋值
            lg.info('mime_type:%s church_prefix%s series_prefix%s' % (settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix'],user.church.code,series))

            if (dkey != ''):
                #删除数据库
                
                MediaFile.objects.filter(name=dkey).delete()
                medias = Media.objects.filter(Q(alioss_video=dkey) | Q(alioss_audio=dkey) |Q(alioss_image=dkey) | Q(alioss_pdf=dkey))
                for md in medias:
                    if md.alioss_video == dkey:
                        md.alioss_video = ''
                    if md.alioss_audio == dkey:
                        md.alioss_audio = ''
                    if md.alioss_image == dkey:
                        md.alioss_image = ''
                    if md.alioss_pdf == dkey:
                        md.alioss_pdf = ''
                    md.save()

            lg.info('mime_type:%s chuAliyunVideoStoragerch_prefix%s series_prefix%s dkey%s  skey%s' % (settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix'],user.church.code,series,dkey,skey))
            qrset = None
            if typ == 'tuwen':
                if skey != '':
                    qrset = WeeklyReport.objects.filter(church=user.church,title__icontains=skey).order_by('-update_time')
                else:
                    qrset = WeeklyReport.objects.filter(church=user.church).order_by('-update_time')
            else:
                if skey != '':
                    qrset = MediaFile.objects.filter(church_prefix=user.church.code,origin_name__icontains=skey,mime_type__startswith=settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix']).order_by('-update_time')
                else:
                    qrset = MediaFile.objects.filter(series_prefix=series,church_prefix=user.church.code,mime_type__startswith=settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix']).order_by('-update_time')

            total = qrset.count()
            pg = Paginator(qrset, 18)
            results = pg.page(page)

            from  ckeditor_uploader import utils 
            from .utils import is_valid_image_extension
            lg.info(typ)
            lg.info(results)
            files = []
            # dirs = set()
            for rc in results :
                if typ == 'tuwen':
                    files.append({
                        'thumb': AliyunMediaStorage.get_media_url('images', rc.image),
                        'src': "http://%s/blog/tuwen/%d" % (request.META['HTTP_HOST'],rc.id),
                        'key':"/blog/tuwen/%d" % rc.id,
                        'is_image': True,
                        'typ':typ,
                        'visible_filename': rc.title,
                    })
                else:
                    filename = rc.name  #bucket key
                
                    key = self._normalize_name(self._clean_name(filename))
                    key = key.encode('utf8')
                    # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
                    from oss2.compat import urlquote,urlparse
                    key = urlquote(key, safe='/?=')
                    p = urlparse(rc.endpoint)

                    media_url = self._media_url(typ,key)#'{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[self.destination]['redirecturl'], key)

                    visible_filename = rc.origin_name
                    if rc.mime_type.startswith( 'image/' ):
                        thumb = '%s?%s' % (media_url,'x-oss-process=style/wh100_auto')#self.get_thumb_filename(media_url)
                    else:
                        from church.confs.base import get_icon_filename
                        thumb = get_icon_filename(visible_filename)

                    files.append({
                        'thumb': thumb,
                        'src': media_url,
                        'key':key,
                        'is_image': is_valid_image_extension(filename),
                        'typ':typ,
                        'visible_filename': visible_filename,
                    })
                
            lg.info('-----get_files_from_db----files---')
            lg.info(files)
            return (files,total)
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e

    def get_image_files(self,user=None, path='',marker = ''):
        return super().get_image_files(user=user,path=path,marker = marker)


    def _set_bucket(self,dest="destination"):
        '''
        这个里面包含了，源桶和目标桶的逻辑。比如。当videos取不到时，取videos的源桶。videos.source
        '''
        if dest not in settings.ALIOSS_DESTINATIONS:
            if '%s.source' % dest not in settings.ALIOSS_DESTINATIONS:
                raise Exception('%s or %s not find the destination bucket' % (dest,'%s.source' % dest))
            else:
                self.destination = '%s.source' % dest
                self.bucket_name = settings.ALIOSS_DESTINATIONS['%s.source' % dest]['bucket']
        else:
            self.destination = dest
            self.bucket_name = settings.ALIOSS_DESTINATIONS[dest]['bucket']
        
        try:
            if self.bucket_name not in super()._list_bucket(self.service):
                # create bucket if not exists
                self.bucket = super()._create_bucket(self.auth)
            else:
                # change bucket acl if not consists
                self.bucket = super()._check_bucket_acl(self._get_bucket(self.auth))
        except AccessDenied:
            # 当启用了RAM访问策略，是不允许list和create bucket的
            self.bucket = super()._get_bucket(self.auth)
    @classmethod
    def get_media_url(cls,dest,key):
        if dest not in settings.ALIOSS_DESTINATIONS:
            raise Exception('dest %s not in ALIOSS_DESTINATIONS' % dest)
        
        enp = settings.ALIOSS_DESTINATIONS[dest]['endpoint'] #
        p = urlparse(enp)
        media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)
        return media_url

    def _media_url(self,dest,key):
        if dest not in settings.ALIOSS_DESTINATIONS:
            raise Exception('dest %s not in ALIOSS_DESTINATIONS' % dest)
        
        enp = settings.ALIOSS_DESTINATIONS[dest]['endpoint'] #
        p = urlparse(enp)
        media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)
        return media_url

    
    # def media_url(self, fn, addUpath=False):
    #     fn = self._normalize_name(self._clean_name(fn))
    #     key = '%s/%s' % (self._get_user_path(None),fn) if addUpath else fn #加入用户的教会目录
    #     key = key.encode('utf8')
    #     # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
    #     # retUrl = self.__url(self.bucket_name, name,safe='/?=')#self.bucket._make_url(self.bucket_name, name,slash_safe=True) 
    #     from oss2.compat import urlquote,urlparse
    #     key = urlquote(key, safe='/?=')
    #     p = urlparse(self.end_point)
    #     return '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[self.destination]['redirecturl'], key)
    
    # def media_url_v2(self,key,addUpath=False,dest="source"):
    #     auth = oss2.Auth(settings.ALIOSS_ACCESS_KEY_ID, settings.ALIOSS_SECRET_ACCESS_KEY)
    #     bucket = oss2.Bucket(auth, settings.ALIOSS_DESTINATIONS[dest]['endpoint'], settings.ALIOSS_DESTINATIONS[dest]['bucket'])
    #     theLogger.info(bucket)

    #     theLogger.info(key)

    #     if not bucket.object_exists(key) :
    #         return "" #不存在文件 返回空

    #     retval = bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)

    #     if bucket.get_object_acl(key).acl ==  oss2.OBJECT_ACL_PUBLIC_READ:
    #         retval = retval.split('?')[0]
    #     else:
    #         pass
    #         #通过nginx来转发，国内国外请求，可以减少费用。但是目前还不是很稳定，所以等后台有了动态配置功能后再实施？
    #     from oss2.compat import urlquote,urlparse
    #     key = urlquote(retval, safe='/?=')
    #     p = urlparse(self.end_point)
    #     return '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)

from oss2.compat import urlquote,urlparse
@deconstructible
class AliyunVideoStorage(AliyunBaseStorage):
    
    location = '/'#settings.MEDIA_ROOT
    destination = "source" #在父类url中使用取得redirect url getattr(self, 'out')# 获取子类的out()方法
    def del_get_media_from_db(self,typ='videos',key=''):
        '''
        从数据库中取单个的媒体对像
        '''
        try:
            if key == '':
                raise Exception(' key should not be null ')
            key = self._normalize_name(self._clean_name(key))
            key = key.encode('utf8')
            # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
            
            key = urlquote(key, safe='/?=')
            dest = self._get_destination(typ)  
            enp = settings.ALIOSS_DESTINATIONS[dest]['endpoint'] #这里得到源桶
            if enp != rc.endpoint :
                raise Exception(' settings and db endpoint not match. ')
            p = urlparse(enp)

            media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)
            signed_url = self.bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
            
            qs = MediaFile.objects.filter(name=key)
            if len(qs) != 1:
                raise Exception(' media record not unique ')

            ro ={
                'thumb': utils.get_icon_filename(qs[0].origin_name),
                'src': signed_url,
                'key':key,
                'is_image': False,
                'typ':typ,
                'visible_filename': qs[0].origin_name,
                'video_status':qs[0].video_file_status,
                'video_tcinfo':qs[0].video_file_tcinfo,
            }
            return ro
            
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e

    def get_mimetype(dest=''):
        for mtype in settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix_arr']:
            str = Q()

        

    
    def get_files_from_db(self,user=None,typ=None,series='',page=1,dkey='',skey=''):
        '''
        从数据库中，查找媒体记录
        '''
        try:
            if typ != 'videos':
                raise Exception(' typ should be videos ')
            self._set_bucket(dest=typ)  #根据不同的媒体 取不同的存储桶 不同的存储桶，目的是为了上传。有不同的访问url，跨国加速url和redirect url  同时会对self.destination进行赋值
            if (dkey != ''):
                #删除上传桶
                # self.bucket.delete_object(dkey)
                #删除video的目标桶
                # vdbk = Bucket(self.auth, settings.ALIOSS_DESTINATIONS['%s.destination']['endpoint.acc'], settings.ALIOSS_DESTINATIONS['%s.destination']['bucket'])
                # vdbk.delete_object(dkey)
                # 目前不删除文件

                #删除数据库
                from django.db.models import Q
                MediaFile.objects.filter(name=dkey).delete()
                medias = Media.objects.filter(Q(alioss_video=dkey) | Q(alioss_audio=dkey) |Q(alioss_image=dkey) | Q(alioss_pdf=dkey))
                for md in medias:
                    if md.alioss_video == dkey:
                        md.alioss_video = ''
                    if md.alioss_audio == dkey:
                        md.alioss_audio = ''
                    if md.alioss_image == dkey:
                        md.alioss_image = ''
                    if md.alioss_pdf == dkey:
                        md.alioss_pdf = ''
                    md.save()

            lg.info('mime_type:%s chuAliyunVideoStoragerch_prefix%s series_prefix%s dkey%s  skey%s' % (settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix'],user.church.code,series,dkey,skey))
            qrset = None
            if skey != '':
                qrset = MediaFile.objects.filter(church_prefix=user.church.code,origin_name__icontains=skey,mime_type__startswith=settings.ALIOSS_DESTINATIONS[self.destination]['mimetype_prefix']).order_by('-update_time')
            else:
                from django.db.models import Q
                qrset = MediaFile.objects.filter(Q(series_prefix=series),Q(church_prefix=user.church.code),Q(mime_type__startswith=settings.ALIOSS_DESTINATIONS['videos.destination']['mimetype_prefix_arr'][0]) | Q(mime_type__startswith=settings.ALIOSS_DESTINATIONS['videos.destination']['mimetype_prefix_arr'][1])).order_by('-update_time')
            lg.info(qrset)

            total = qrset.count()
            pg = Paginator(qrset, 18)
            results = pg.page(page)

            from  ckeditor_uploader import utils 
            from .utils import is_valid_image_extension
            
            files = []
            # dirs = set()
            update_list = []
            for rc in results :
                filename = rc.name  #bucket key
                key = self._normalize_name(self._clean_name(filename))
                key = key.encode('utf8')
                # 做这个转化，是因为下面的_make_url会用urllib.quote转码，转码不支持unicode，会报错，在python2环境下。
                
                key = urlquote(key, safe='/?=')
                dest = self._get_destination(typ)  
                enp = settings.ALIOSS_DESTINATIONS[dest]['endpoint'] #这里得到源桶
                if enp != rc.endpoint :
                    raise Exception(' settings and db endpoint not match. ')
                p = urlparse(enp)

                media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)
                signed_url = self.bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)
                
                '%s.destination' % typ
                tcinfo ={"image1": "00001.jpg", "image2": "00002.jpg", "image3": "00003.jpg", "sd": "sd.mp4", "hd": "hd.mp4", "ld": "ld.mp4", "audio": "ld.mp4"}
                tcinfo['image1'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['image1']))
                tcinfo['image2'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['image2']))
                tcinfo['image3'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['image3']))
                tcinfo['sd'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['sd']))
                tcinfo['hd'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['hd']))
                tcinfo['ld'] = self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['ld']))
                tcinfo['audio'] =self._media_url('%s.destination' % typ,'%s/%s' % (key,tcinfo['audio']))

                if rc.video_file_status != 3 :
                    try:
                        with urllib.request.urlopen(tcinfo['sd']) as f:
                            if f.status == 200:
                                rc.video_file_status = 3
                                update_list.append(rc.id)

                    except Exception as e:
                        theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)

                   
                #视频需求返回的数据有源桶的signed_url,只要存在就可以；2 要返回状态 3 返回redirecturl
                #images只要返回thumb src 
                visible_filename = rc.origin_name
                thumb = utils.get_icon_filename(visible_filename)

                files.append({
                    'thumb': thumb,
                    'src': signed_url,
                    'key':key,
                    'is_image': False,
                    'typ':typ,
                    'visible_filename': visible_filename,
                    'video_status':rc.video_file_status,
                    'video_tcinfo':tcinfo,
                })

            if len(update_list) > 0 :
                MediaFile.objects.filter(id__in=update_list).update(video_file_status=3)
                
            # lg.info('last (files dirs):')
            # lg.info((files,dirs))
            lg.info('-----get_files_from_db----files---')
            lg.info(files)
            return (files,total)
        except Exception as e:
            theLogger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    def _media_url(self,dest,key):
        if dest not in settings.ALIOSS_DESTINATIONS:
            raise Exception('dest %s not in ALIOSS_DESTINATIONS' % dest)
        
        enp = settings.ALIOSS_DESTINATIONS[dest]['endpoint'] #
        p = urlparse(enp)
        media_url = '{0}://{1}/{2}'.format(p.scheme,settings.ALIOSS_DESTINATIONS[dest]['redirecturl'], key)
        return media_url

        # signed_url = self.bucket.sign_url('GET', key, settings.ALIOSS_EXPIRES)

    def _get_destination(self,dest="destination"):
        '''
        '''
        return '%s.source' % dest

    def _set_bucket(self,dest="destination"):
        '''
        这个里面包含了，源桶和目标桶的逻辑。比如。当videos取不到时，取videos的源桶。videos.source
        '''
        if dest not in settings.ALIOSS_DESTINATIONS:
            if '%s.source' % dest not in settings.ALIOSS_DESTINATIONS:
                raise Exception('%s or %s not find the destination bucket' % (dest,'%s.source' % dest))
            else:
                self.destination = '%s.source' % dest
                self.bucket_name = settings.ALIOSS_DESTINATIONS['%s.source' % dest]['bucket']
        else:
            self.destination = dest
            self.bucket_name = settings.ALIOSS_DESTINATIONS[dest]['bucket']
        
        try:
            if self.bucket_name not in super()._list_bucket(self.service):
                # create bucket if not exists
                self.bucket = super()._create_bucket(self.auth)
            else:
                # change bucket acl if not consists
                self.bucket = super()._check_bucket_acl(self._get_bucket(self.auth))
        except AccessDenied:
            # 当启用了RAM访问策略，是不允许list和create bucket的
            self.bucket = super()._get_bucket(self.auth)

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
