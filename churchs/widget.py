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
# from urllib import urlencode

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
        # js = ('/static/lib/plupload-2.1.2/js/plupload.full.min.js','/static/upload.js' )
        css = {'all': ('/static/ossstyle.css', )}

    def __init__(self, *args, **kwargs):
        self.dest = kwargs.pop('dest', None)
        self.fieldname = kwargs.pop('fieldname', None)
        super(AliOssDirectWidgetExt, self).__init__(*args, **kwargs)


    def render(self, name, value, **kwargs):
        file_url = value or ''
        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')

        # pprint.PrettyPrinter(4).pprint(self)
        # pprint.PrettyPrinter(4).pprint(name)
        # pprint.PrettyPrinter(4).pprint(value)
        # pprint.PrettyPrinter(4).pprint(kwargs)

        ctx = {
            # 'policy_url': reverse('s3direct'),
            # 'signing_url': reverse('s3direct-signing'),
            # 'dest': self.dest,
            # 'name': name,
            # 'csrf_cookie_name': csrf_cookie_name,
            'file_url': file_url,
            # 'file_name': os.path.basename(urlunquote_plus(file_url)),
            # 'test':'test_1',
            'name':name,
            'fieldname':self.fieldname
        }

        return mark_safe(
            render_to_string( 'admin/aliossdirect-widget.tpl',
                             ctx))


class AliOssDirectField(Field):
    def __init__(self, *args, **kwargs):
        dest = kwargs.pop('dest', None)
        fn = kwargs.pop('fieldname', None)
        self.widget = AliOssDirectWidgetExt(dest=dest,fieldname=fn)
        super(AliOssDirectField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(AliOssDirectField, self).formfield(*args, **kwargs)
    def to_python(self,value):
        if not value:
            value=[]
        if isinstance(value,list):
            return value
        return urllib.parse.unquote(value)
    def get_prep_value(self, value):
        if value is None:
            return value
        return urllib.parse.quote(value)   #存储为url
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return urllib.parse.unquote(self.get_db_prep_value(value))



# class 