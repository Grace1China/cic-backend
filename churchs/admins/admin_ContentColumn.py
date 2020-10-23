# from churchs.admins.admin_ContentColumn import ContentColumnAdmin
from django.forms import modelformset_factory
from django.forms.formsets import BaseFormSet, formset_factory
from churchs.form.column import ColChangeListForm, ContentColumnForm
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

from django.utils.html import format_html
from church.confs.prod import get_ALIOSS_DESTINATIONS
import logging

loger = logging.getLogger('church.all')


class ColumnMediasForm(forms.ModelForm):
    '''------------------------------------
    Ver 1
    多选组件好的部分是他的修改联动 在form的保存时，修改调用者窗口的修改方法
    新增是不需要的  XX
    删除是要重新定义， 要改成是只删除关联表项  这个需要一个callback删除后台，然后又更新前面的组件
    图片和链接要链接到浏览页面
    ------------------------
    Ver 2
    自已做，有赞是换了页面。回退回来就是一个正确的状态。在form的保存时，修改调用者窗口的修改方法
    删除是不需要有提示页面的。只是把选择的关联断开就可以了。
    图片和链接要链接到浏览页面
    还有一个序号的问题
    -------------------------------------------
    Ver 3
    保留目前的多选组件，图片和链接
    -----------------------
    Ver 4 
    保留图片 链接 和跳转本页方式的修改
    '''
    Media = forms.ModelChoiceField(
        label="", queryset=Media.objects.all(), widget=HiddenInput, required=False)

    class Meta:
        model = ColumnMedias
        exclude = ()
        show_url = False

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)


class ColumnMediasInline(admin.TabularInline):
    form = ColumnMediasForm
    model = ColumnMedias
    template = 'admin/churchs/content_tabular.html'
    # 'Media_cover','Media_link','Media_edit','Media_delete'
    readonly_fields = ('Media_one',)
    ordering = ('order', '-Media__pub_time',)
    extra = 0
    can_delete = False

    # max_num = 4
    # min_num = 1

    def Media(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<input type="hidden" name='Media' value="{}" >''',
            instance.Media,
        )

    # short_description functions like a model field's verbose_name
    # Media_cover.short_description = ""

    def get_kind_title(self, kind):
        if kind == 'video' or kind == '6':
            kind = '视频'
        elif kind == 'audio' or kind == '7':
            kind = '音频'
        elif kind == 'tuwen' or kind == '8':
            kind = '图文'
        else:
            raise Exception('no support %s' % kind)
        return kind

    def Media_one(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<div style="width:100%;display:flex;align-items: center;">
            <img data-name="cover" style="height: 100px;width: 177.59px;flex-grow: 0;text-align: left;margin-left: 20px;" src="{}" @click="popupCenter('/admin/churchs/media/?mediaid={}','媒体库',900,600)">
            <span  style="flex-grow: 1;text-align: left;margin-left: 20px;">{}</span>
            <a data-name="title" style="flex-grow: 1;text-align: left;margin-left: 20px;" target="_blank" type="text" href="/blog/media/{}" >{}</a>
            <a data-name="edit" style='flex-grow: 0;margin-left: 20px;' href="/admin/churchs/media/{}/change/?kind={}" target="_blank">{}</a>
            <el-button data-name="delete" style='flex-grow: 0;margin-left: 20px;' type="text" @click="deleteContent({},{})">{}</el-button>
            </div>
            ''',
            'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ='images')
                              ['redirecturl'], instance.Media.alioss_image),
            instance.Media,
            self.get_kind_title(str(instance.Media.kind)),
            instance.Media.id,
            instance.Media.title,
            instance.Media.id,
            instance.Media.kind,
            "编辑",
            instance.ContentColumn.id,
            instance.Media.id,
            "删除"
        )

    # short_description functions like a model field's verbose_name
    Media_one.short_description = ""

    def Media_cover(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<img style="height: 100px;width: 177.59px;" src="{}" @click="popupCenter('/admin/churchs/media/?mediaid={}','媒体库',900,600)">''',
            'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ='images')
                              ['redirecturl'], instance.Media.alioss_image),
            instance.Media,
        )

    # short_description functions like a model field's verbose_name
    Media_cover.short_description = ""

    def Media_link(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<a @click="popupCenter('/admin/churchs/media/{}/change/?_to_field=id&_popup=1')" href="javascript:void(0)">{}</a>''',
            instance.Media.id,
            instance.Media.title
        )

    Media_link.short_description = ""

    def Media_edit(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<a @click="popupCenter('/admin/churchs/media/{}/change/?_to_field=id&_popup=1')" href="javascript:void(0)">{}</a>''',
            instance.Media.id,
            "编辑"
        )

    Media_edit.short_description = ""

    # short_description functions like a model field's verbose_name

    def Media_delete(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<el-button type="text" @click="store.dispatch('delete',{})">{}</el-button>''',
            instance.Media.id,
            "删除"
        )

    Media_delete.short_description = ""


# from app.models import Movie


class ColChangeList(ChangeList):
    def __init__(self, request, model, list_display,
                 list_display_links, list_filter, date_hierarchy,
                 search_fields, list_select_related, list_per_page,
                 list_max_show_all, list_editable, model_admin, sortable_by):
        super(ColChangeList, self).__init__(request, model,
                                            list_display, list_display_links, list_filter,
                                            date_hierarchy, search_fields, list_select_related,
                                            list_per_page, list_max_show_all, list_editable,
                                            model_admin, sortable_by)

        # these need to be defined here, and not in MovieAdmin
        self.list_display = ['action_checkbox', 'title', 'cover', 'pub_time',
                             'status', 'parentCol', ]
        self.list_display_links = ['title']
        self.list_editable = ['cover', 'parentCol']


# class BaseColFormSet(BaseModelFormSet):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.queryset = ContentColumn.objects.all()

import pickle


class ColAdmin(admin.ModelAdmin):
    form = ContentColumnForm
    model = ContentColumn

    def get_changelist(self, request, **kwargs):
        return ColChangeList

    def get_changelist_form(self, request, **kwargs):
        return ColChangeListForm

    def get_changelist_formset(self, request, **kwargs):
        kwargs['formset'] = modelformset_factory(
            ContentColumn, form=ColChangeListForm)
        return super().get_changelist_formset(request, **kwargs)

    # 
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     loger.info('---------formfield_for_foreignkey--------')
    #     loger.info('---------formfield_for_foreignkey--------')
    #     loger.info('---------formfield_for_foreignkey--------')
    #     if db_field.name == "parentCol":
    #         qs = ContentColumn.objects.filter(church=request.user.church)
    #         # qs.query = pickle.loads(pickle.dumps(qs.query))
    #         loger.info(qs)
    #         loger.info(qs.query)
    #         kwargs["queryset"] = qs
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     loger.info('---------get_form--------')
    #     kwargs['form'] = ContentColumnForm
    #     return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data['cover'] != obj.cover:
            obj.cover = form.cleaned_data['cover']
        if form.cleaned_data['parentCol'] != obj.parentCol:
            obj.parentCol = form.cleaned_data['parentCol']
        obj.church = request.user.church
        obj.user = request.user
        obj.save()

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

    fieldsets = (
        (None, {
            'fields': ('title', 'pub_time', 'status', 'cover', 'add_content')
        },),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('parentCol', 'content',),
        },),
    )
    
    def get_changeform_initial_data(self, request):
        loger.info('-------get_changeform_initial_data-----------')
        return {'user': request.user.id, 'church': request.user.church,
                'status': churchs_models.ContentColumn.STATUS_CLOSE}

    # def get_fields(self, request, obj=None):
    #     try:
    #         # theLogger.info(obj.__dict__)
    #         fieldsets = (
    #             (None, {
    #                 'fields': ('title', 'pub_time', 'status', 'cover', 'add_content',),
    #             },),
    #             ('Advanced options', {
    #                 'classes': ('collapse',),
    #                 'fields': ('parentCol', 'content',),
    #             },),
    #         )
    #         return fieldsets
    #     except Exception as e:
    #         import traceback
    #         loger.exception('There is and exceptin', exc_info=True, stack_info=True)
    #         raise e
    readonly_fields = ('add_content',)
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

    change_form_template = "admin/churchs/change_form_content.html"

    # short_description functions like a model field's verbose_name
    add_content.short_description = "批量添加内容"

    inlines = [
        ColumnMediasInline,
    ]

admin.site.register(churchs_models.ContentColumn, ColAdmin)


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
