from django.contrib import admin
from churchs.models import WeeklyReport, Sermon, Media,SermonSeries,Speaker
from churchs import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from churchs.widget import AliVideoWidgetExt
from django.forms import ModelForm,Form
from churchs.widget import S3DirectField,AliOssDirectField,AliOssDirectWidgetExt,AliMediaWidgetExt,MediaBaseWidget
from churchs.forms import MeidaForm2
from users.models import CustomUser
from church.models import Church
from churchs.models.vpage import vpage_position

from django import forms
from django.db.models import Q
from django.forms import widgets as Fwidgets
from django.forms import fields
from django.forms.widgets import HiddenInput

from django.utils.html import format_html
from church.confs.prod import get_ALIOSS_DESTINATIONS
import logging
loger = logging.getLogger('church.all')

from datetime import datetime

class Vpage_position_Form(forms.ModelForm):
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
    # content = forms.t(label="",queryset=Media.objects.all(),widget=HiddenInput,required=False)
    vposition = forms.ModelChoiceField(label="微组件",queryset=vpage_position.objects.all(),required=False)
    class Meta:
        model = vpage_position
        exclude = ()

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

class vpage_positionInline(admin.TabularInline):
    form = Vpage_position_Form
    model = vpage_position
    fields = ('vposition',)
    readonly_fields = ('content1',)


    def content1(self, instance):
        return format_html(
            '''<div contentEditable='True' style="width:100%;display:flex;align-items: center;">
            {}
            </div>
            ''',
            '文字内容'
        ) 
    # template = 'admin/churchs/content_tabular.html'
    # readonly_fields = ('content',)  #'Media_cover','Media_link','Media_edit','Media_delete'
    
    extra = 0
    can_delete = False
    # max_num = 4
    # min_num = 1

class VpageAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)


    list_display = ('title','name', 'pub_time','promote_at','status','promote')  
    # list_filter = (MediaKindListFilter, 'alioss_video_status')
    fields = ('title','name', 'pub_time','promote_at','status')
    

    formfield_overrides = {
        churchs_models.Media.content: {'widget': CKEditorWidget()},
    }

    def promote(self, obj):
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,"%s")'>推广链接</a>
        <a class="changelink" href="/admin/churchs/vpage/%d/change/">编辑</a>""" % (obj.id,'touvideo',obj.id)
        return format_html(button_html)
    promote.short_description = "操作"
    
    def get_changeform_initial_data(self, request):
        pass


    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        instance.create_by = request.user
        instance.church = request.user.church

        return instance

    inlines = [
        vpage_positionInline,
    ]




    

    