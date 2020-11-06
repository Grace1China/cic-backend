# from churchs.admins.admin_ContentColumn import ContentColumnAdmin
from django.forms import modelformset_factory
from django.forms.formsets import BaseFormSet, formset_factory
from churchs.form.column import ColChangeListForm, ContentColumnForm, ColumnMediasInline
from django.contrib.admin.views.main import ChangeList
from churchs.models import ColumnMedias
from django.contrib import admin
from churchs.models import WeeklyReport, Sermon, Media, SermonSeries, Speaker
from churchs import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from churchs.widget import AliVideoWidgetExt
from django.forms import ModelForm, Form
from churchs.widget import S3DirectField, AliOssDirectField, AliOssDirectWidgetExt, AliMediaWidgetExt, MediaBaseWidget
from churchs.forms import MeidaForm2
from users.models import CustomUser
from church.models import Church
from churchs.models.columnContent import ContentColumn

from django import forms
from django.db.models import Q
from django.forms import widgets as Fwidgets
from django.forms import fields
from django.forms.widgets import HiddenInput, Select, Textarea

from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
from django.utils.html import format_html
from church.confs.prod import get_ALIOSS_DESTINATIONS
import logging

loger = logging.getLogger('church.all')

class ContentColumnAdmin(admin.ModelAdmin):
    form = ContentColumnForm

    class Media:
        js = ("admin/js/jquery.init.js",)

    change_form_template = "admin/churchs/change_form_content.html"

    list_display = ('title_with_link', 'pub_time', 'status',
                    'parentCol_with_link', 'promote',)
    fieldsets = (
        (None, {
            'fields': ('title', 'pub_time', 'status', 'cover', 'add_content')
        },),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('parentCol', 'content',),
        },),
    )

    readonly_fields = ('add_content',)

    def title_with_link(self, obj):
        return format_html(
            '<a target="_blank" href="/blog/ccol/{}">{}</a>',
            obj.id,
            obj.title,
        )

    title_with_link.short_description = '标题'

    def parentCol_with_link(self, obj):
        return format_html(
            '<a target="_blank" href="/admin/churchs/contentcolumn/{}/change/">{}</a>',
            obj.parentCol.id,
            obj.parentCol.title,
        )

    title_with_link.short_description = '标题'

    def add_content(self, instance):
        # assuming get_full_address() returns a list of strings
        # for each line of the address and you want to separate each
        # line by a linebreak
        if instance.id is None:
            return format_html(

                '''<el-button disabled @click="popupCenter('/admin/churchs/media/?kind=6&frompage=content_column&columnid={}','媒体库',900,600)">{}</el-button>''',
                0,
                '批量添加内容,先保存专栏'
            )
        else:
            return format_html(

                '''<el-button @click="popupCenter('/admin/churchs/media/?kind=6&frompage=content_column&columnid={}','媒体库',900,600)">{}</el-button>''',
                instance.id,
                '批量添加内容'
            )

    # short_description functions like a model field's verbose_name
    # add_content.short_description = "批量添加内容"

    inlines = [
        ColumnMediasInline,
    ]

    # formfield_overrides = {
    #     churchs_models.Media.content: {'widget': CKEditorWidget()},
    # }

    # def promote(self, obj):
    #     button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,"%s")'>推广链接</a>""" % (obj.id,'touvideo')
    #     return format_html(button_html)
    # promote.short_description = "操作"

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            qs = qs.filter(church=request.user.church)
            loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',
                            exc_info=True, stack_info=True)
            raise e

    def get_changeform_initial_data(self, request):
        return {'user': request.user.id, 'church': request.user.church,
                'status': churchs_models.ContentColumn.STATUS_CLOSE}

    def save_form(self, request, form, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        instance.user = request.user
        instance.church = request.user.church
        return instance

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parentCol":
            kwargs["queryset"] = ContentColumn.objects.filter(church=request.user.church)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def promote(self, obj):

        button_html = """<a class="changelink" href="/admin/churchs/contentcolumn/%d/change/">编辑</a>""" % (
            obj.id)
        return format_html(button_html)

    promote.short_description = "操作"

    #

# admin.site.register(churchs_models.ContentColumn, ContentColumnAdmin)
