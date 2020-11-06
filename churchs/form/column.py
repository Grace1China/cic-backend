from django.contrib import admin
from django.forms import HiddenInput, TypedChoiceField
from django.utils.html import format_html

from church.confs.base import get_ALIOSS_DESTINATIONS
from churchs.models import ColumnMedias, Media, CustomUser
from churchs.models.columnContent import ContentColumn
from django import forms
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


import logging
from churchs.widget import MediaBaseWidget
loger = logging.getLogger('church.all')
from django.db.models import Q

import pickle

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


  
class ColChangeListForm(forms.ModelForm):
    # parentCol = forms.ModelChoiceField(queryset=ContentColumn.objects.none(), required=False)
    parentCol = TypedChoiceField(choices=(), coerce=int, required=False)
    cover = forms.CharField(widget=MediaBaseWidget(label='', typ='images'), required=False)
    
    class Meta:
        model = ContentColumn
        fields = '__all__'
        exclude = ['medias','content','user']
    def _getCacheCols(self,churchid=-1):
        lsCol = []
        if 'church:%d_column' % churchid in cache and cache.get('church:%d_column' % churchid) != None:
            # get results from cache
            lsCol = cache.get('church:%d_column' % churchid)
        else:
            cols = ContentColumn.objects.values_list('id','title').filter(church=churchid)
            lsCol = list(cols)
            # store data in cache
            lsCol.insert(0,('', '-------------'))
            cache.set('church:%d_column' % churchid, lsCol, timeout=CACHE_TTL)
        return lsCol
    def __init__(self, *args, **kwargs):
        loger.info(kwargs)
        super(ColChangeListForm, self).__init__(*args, **kwargs)
        CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
        
        
        if self.instance and self.instance.id:
            loger.info(self.instance.__dict__)
            # self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=self.instance.church).filter(~Q(id=self.instance.id))
            lsCol =self._getCacheCols(self.instance.church.id)
            lsCol.remove((self.instance.id, self.instance.title))
            
            self.fields['parentCol'].choices = lsCol
        elif kwargs.__contains__('initial'):
            lsCol =self._getCacheCols(kwargs['initial']['church'].id) 
            self.fields['parentCol'].choices = lsCol
            # self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=kwargs['initial']['church'].id)
        elif args[0]['parentCol']:
            pass
            # self.fields['parentCol'].queryset = ContentColumn.objects.filter(id=int(args[0]['parentCol']))
            


class ContentColumnForm(forms.ModelForm):

    cover = forms.CharField(label="", widget=MediaBaseWidget(label='封面', typ='images'), required=False)
    parentCol = forms.ModelChoiceField(label='父专栏', queryset=ContentColumn.objects.none(), required=False)

    # parentCol = forms.ModelChoiceField()
    class Meta:
        model = ContentColumn
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ContentColumnForm, self).__init__(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        loger.info('-----ContentColumnForm-----------')
        loger.info(kwargs)
        super(ContentColumnForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=self.instance.church).filter(~Q(id=self.instance.id))
        elif kwargs.__contains__('initial'):
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=kwargs['initial']['church'].id)
        elif args[0]['parentCol']:#here is for 
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(id=int(args[0]['parentCol']))

# 
# def create_model_form(request,admin_class):
#     '''动态生成Model Form'''
# 
#     # 修改样式
#     def __new__(cls, *args, **kwargs):
#         #print(cls.base_fields)     OrderedDict([('name', <django.forms.fields.CharField object at 0x000001385625DA90>)]),
#         for field_name,field_obj in cls.base_fields.items():
#             # 根据 cls.base_field 的特性给每个字段加上样式
#             cls.base_fields[field_name].widget.attrs['class'] = 'form-control'
# 
#         return forms.ModelForm.__new__(cls)
# 
#     class Meta:
#         model = admin_class.model        # 通过admin_class动态获取model
#         # fields = ('name', 'qq')        # 可以获取指定字段
#         # age = forms.IntegerField()     # 还可以添加字段
#         parentCol = forms.ModelChoiceField(
#             queryset=ContentColumn.objects.all(), required=False)
#         fields = '__all__'               # '__all__'获取所有字段
# 
#     attrs = {'Meta':Meta}
# 
#     _model_form_class = type("DynamicModelForm", (forms.ModelForm,), attrs)     # 第一个参数是类名，第二个参数是元组，填写父类，最后必须添加逗号，
#                                                                                 #  第三个参数字典形式的Meta类
#     # 方法一定要 setattr  
#     setattr(_model_form_class,'__new__',__new__)
#     return _model_form_class    # 返回的是一个类
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


