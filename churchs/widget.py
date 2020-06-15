from s3direct.widgets import S3DirectWidget
import boto3
from django.conf import settings
import os
from django.forms.widgets import TextInput
from django.db.models import Field
from django.urls import reverse
from django.utils.http import urlunquote_plus
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
import pprint
import urllib
import django.conf
# from urllib import urlencode
from api.utill import CICUtill

import logging 
theLogger = logging.getLogger('church.all')

class S3DirectWidgetExt(TextInput):
    class Media:
        js = ('s3direct/dist/index.js', )
        css = {'all': ('s3direct/dist/index.css', )}

    def __init__(self, *args, **kwargs):
        self.dest = kwargs.pop('dest', None)
        super(S3DirectWidgetExt, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        file_url = value or ''
        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')

        ctx = {
            'policy_url': reverse('s3direct'),
            'signing_url': reverse('s3direct-signing'),
            'dest': self.dest,
            'name': name,
            'csrf_cookie_name': csrf_cookie_name,
            'file_url': file_url,
            'file_name': os.path.basename(urlunquote_plus(file_url)),
        }

        return mark_safe(
            render_to_string( 'admin/s3direct-widget.tpl',
                             ctx))


class S3DirectField(Field):
    def __init__(self, *args, **kwargs):
        dest = kwargs.pop('dest', None)
        self.widget = S3DirectWidgetExt(dest=dest)
        super(S3DirectField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(S3DirectField, self).formfield(*args, **kwargs)




class AliOssDirectWidgetExt(TextInput):
    class Media:
        import time
        ticks = time.time()
        # js = ('/static/lib/plupload-2.1.2/js/plupload.full.min.js','/static/upload.js' )
        css = {'all': ('%s?v=%d' % ('/static/ossstyle.css?v=',int(ticks)), )}

    def __init__(self, *args, **kwargs):
        self.dest  = kwargs.pop('dest', None)
        self.fieldname = kwargs.pop('fieldname', None)
        self.vbn = kwargs.pop('label',None)
        
        super(AliOssDirectWidgetExt, self).__init__(*args, **kwargs)
        # 要处理的问题是：在前面只要是<churchs.widget.AliOssDirectWidgetExt, 并且要在widget中显示label


    def render(self, name, value, **kwargs):
        # from api.utill import CICUtill
        file_url = value or ''  #目前这个是bucket的key
        file_url = urllib.parse.unquote(file_url)
        theLogger.info(self.fieldname)
        theLogger.info(file_url)
        theLogger.info(name)

        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')
        

        ctx = {
            'file_url': CICUtill.getObjectKey(file_url),#urllib.parse.unquote(file_url), file_url is an url here get the key
            'signed_url':file_url,#if a public not signed but give it so
            'name':name,
            'vbn':self.vbn,
            'fieldname':self.fieldname,
            'acl':settings.ALIOSS_DESTINATIONS[self.dest]['x-oss-object-acl'],
            'public':(file_url != '') and (not file_url.find('Expires=')>=0) ,  
            'public_url':file_url,#if an signed url give it so


        }

        return mark_safe(render_to_string( 'admin/aliossdirect-widget.tpl',ctx))


class AliOssDirectField(Field):
    def __init__(self, *args, **kwargs):
        self.dest = kwargs.pop('dest', None)
        self.fn = kwargs.pop('fieldname', None)
        # self.vbn = kwargs.pop('verbose_name', None)
        # self.label = kwargs.pop('verbose_name', None)
        # pprint.PrettyPrinter(6).pprint('===========verbose_name=====================')

        # pprint.PrettyPrinter(6).pprint(kwargs.get('verbose_name', None))
        # pprint.PrettyPrinter(6).pprint(kwargs.get('verbose_name', None))
        # pprint.PrettyPrinter(6).pprint(kwargs.get('verbose_name', None))

        
        self.widget = AliOssDirectWidgetExt(dest=self.dest,fieldname=self.fn,label=kwargs.get('verbose_name', None))
        super(AliOssDirectField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(AliOssDirectField, self).formfield(*args, **kwargs)




class AliVideoField(Field):
    def __init__(self, *args, **kwargs):
        dest = kwargs.get('dest', None)
        fn = kwargs.get('fieldname', None)
        self.widget = AliVideoWidgetExt(dest=dest,fieldname=fn)
        super(AliOssDirectField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(AliVideoField, self).formfield(*args, **kwargs)


class AliVideoWidgetExt(TextInput):
    class Media:
        # js = ('/static/lib/plupload-2.1.2/js/plupload.full.min.js','/static/upload.js' )
        # css = {'all': ('/static/ossstyle.css', )}
        pass
    def __init__(self, *args, **kwargs):
        self.dest  = kwargs.pop('dest', None)
        self.fieldname = kwargs.pop('fieldname', None)
        self.label = kwargs.pop('label', None)
        # self.public = kwargs.pop('public', None)
        super(AliVideoWidgetExt, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        
        file_url = value or ''  #目前这个是bucket的key
        # file_url = urllib.parse.unquote(file_url)
        
        # signed_url = CICUtill.signurl1(file_url,dest=self.dest)
        
        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')

        ctx = {
            'file_url': file_url,
            'signed_url':file_url,
            'name':name,
            'fieldname':self.fieldname,
            'public': not file_url.find('Expires=')>=0,
            'public_url':file_url ,
            'label':self.label,
            'class':self.attrs['class']
,
        }

        return mark_safe(render_to_string( 'admin/video-wedget.tpl',ctx))



class AliMediaField(Field):
    def __init__(self, *args, **kwargs):
        dest = kwargs.get('dest', None)
        fn = kwargs.get('fieldname', None)
        self.widget = AliMediaWidgetExt()
        super(AliMediaField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(AliMediaField, self).formfield(*args, **kwargs)

class AliMediaWidgetExt(TextInput):
    class Media:
        # js = ('/static/lib/plupload-2.1.2/js/plupload.full.min.js','/static/upload.js' )
        # css = {'all': ('/static/ossstyle.css', )}
        pass
    def __init__(self, *args, **kwargs):
        super(AliMediaWidgetExt, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        
        value = value or ''  
        
        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')

        ctx = {
            'value': value,
            'name':name,
        }

        return mark_safe(render_to_string( 'admin/AliossMedia-wedget.tpl',ctx))


class MediaBaseField(Field):
    def __init__(self, *args, **kwargs):
        self.widget = MediaBaseWidget(label=kwargs.get('verbose_name', None))
        super(MediaBaseField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(MediaBaseField, self).formfield(*args, **kwargs)


class MediaBaseWidget(TextInput):
    class Media:
        pass

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.typ = kwargs.pop('typ', None)

        super(MediaBaseWidget, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        ctx = {
            'typ':self.typ,
            'label':self.label,
            'name':name,
            'value':'' if value is None else value
        }
        theLogger.info(mark_safe(render_to_string( 'admin/media-select.tpl',ctx)))
        return mark_safe(render_to_string( 'admin/media-select.tpl',ctx))


class MediaContentField(Field):
    def __init__(self, *args, **kwargs):
        self.widget = MediaContentField(label=kwargs.get('verbose_name', None))
        super(MediaContentField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(MediaContentField, self).formfield(*args, **kwargs)


class MediaContentWidget(TextInput):
    class Media:
        pass

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.typ = kwargs.pop('typ', None)
        self.cover = kwargs.pop('cover', None)


        super(MediaContentWidget, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        ctx = {
            'typ':self.typ,
            'label':self.label,
            'name':name,
            'value':'' if value is None else value,
            'cover':'' if self.cover is None else self.cover,
        }
        # theLogger.info(mark_safe(render_to_string( 'admin/content-select.tpl',ctx)))
        return mark_safe(render_to_string( 'admin/content-select.tpl',ctx))

