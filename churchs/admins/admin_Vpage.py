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
from churchs.models.vpage import VComponents,VPageComponents,VParts

from django import forms
from django.db.models import Q
from django.forms import widgets as Fwidgets
from django.forms import fields
from django.forms.widgets import HiddenInput
# from django.utils.functional import curry

from django.utils.html import format_html
from church.confs.prod import get_ALIOSS_DESTINATIONS
import logging
theLogger = logging.getLogger('church.all')
loger = logging.getLogger('church.all')


from datetime import datetime

class VPageComponentForm(forms.ModelForm):
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
    components = forms.ModelChoiceField(label="微组件",queryset=VComponents.objects.all(),required=False)
    # church = forms.ModelChoiceField(label="教会",queryset=Church.objects.all(),required=False)
    # create_by = forms.ModelChoiceField(label="用户",queryset=CustomUser.objects.all(),required=False)
    # content = forms.Field(label="富文本", required=False)

    class Meta:
        model = VPageComponents
        exclude = ()
        show_url = False

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        # self.initial = kwargs.get('initial', None)
        # theLogger.info('-------------Vpage_position_Form----__init__-----------')
        # theLogger.info(self.initial)
        # theLogger.info(instance)
        super().__init__(*args, **kwargs)
        


# from django.forms import models
# class vpos_FormSet(models.BaseInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         super(vpos_FormSet, self).__init__(*args, **kwargs)

#         theLogger.info(kwargs['instance'])
#         self.initial = theLogger.info(kwargs['initial'])
#         instance = kwargs['instance']
#         # for form in self.forms:
#         # Check that the data doesn't already exist
#         if not instance.vpage_position_set.filter(vpage=instance.id):
#             theLogger.info(kwargs['initial'])
#             self.initial = kwargs['initial']
#             self.extra += len(self.initial)

    # def save(self, commit=True):
    #     """
    #     Save model instances for every form, adding and changing instances
    #     as necessary, and return the list of instances.
    #     """
    #     theLogger.info(self.initial)
    #     theLogger.info(commit)
    #     if not commit:
    #         self.saved_forms = []

    #         def save_m2m():
    #             for form in self.saved_forms:
    #                 theLogger.info(form)
    #                 form.save_m2m()
    #         self.save_m2m = save_m2m
    #     return self.save_existing_objects(commit) + self.save_new_objects(commit)

    # def save_new(self, form, commit=True):
    #     # Ensure the latest copy of the related instance is present on each
    #     # form (it may have been saved after the formset was originally
    #     # instantiated).
    #     instance = form.save(commit=False)
    #     theLogger.info(instance)
    #     theLogger.info(self.initial)
    #     instance.church = self.initial.church
    #     instance.create_by = self.initial.create_by
    #     setattr(form.instance, self.fk.name,instance)
    #     return instance#super().save_new(form, commit=commit)

class VComponentsInline(admin.TabularInline):
    form = VPageComponentForm
    model = VPageComponents
    # formset = vpos_FormSet
    # template = 'admin/churchs/vpage_tabular.html'
    fields = ('components','order')
    ordering = ('order',)
    extra = 1
    can_delete = True
    # max_num = 4
    # min_num = 1
    # readonly_fields = ('church','create_by',)

    # def get_formset(self, request, obj=None, **kwargs):
    #     initial = []
    #     # if request.method == "GET":
    #     theLogger.info('---------get_formset---------')

    #     initial.append({
    #         'church': request.user.church,
    #         'create_by':request.user
    #     })
    #     initial.append({
    #         'church': request.user.church,
    #         'create_by':request.user
    #     })
    #     initial.append({
    #         'church': request.user.church,
    #         'create_by':request.user
    #     })
    #     theLogger.info(initial)
    #     formset = super(vpos_Inline, self).get_formset(request, obj, **kwargs)
    #     theLogger.info(formset)

    #     formset.__init__ = curry(formset.__init__, initial=initial)
    #     theLogger.info(formset)


    #     return formset


    # def content1(self, instance):
    #     return format_html(
    #         '''<div contentEditable='True' style="width:100%;display:flex;align-items:center;">
    #         {}
    #         </div>
    #         ''',
    #         '文字内容'
    #     ) 
    
    

   

class VPageAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)


    list_display = ('title','name', 'pub_time','promote_at','status','promote')  
    # list_filter = (MediaKindListFilter, 'alioss_video_status')
    fields = ('title','name', 'pub_time','promote_at','status')
    
    # change_form_template ="admin/churchs/change_form_page.html"

    formfield_overrides = {
        churchs_models.Media.content: {'widget': CKEditorWidget()},
    }

    def promote(self, obj):
        button_html = """<a class="changelink" href="/admin/churchs/vpage/%d/change/">编辑</a>""" % obj.id
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
        inlines = self.get_formsets_with_inlines(request,instance)
        theLogger.info(inlines)

        return instance

    def save_related(self, request, form, formsets, change):
        """
        Given the ``HttpRequest``, the parent ``ModelForm`` instance, the
        list of inline formsets and a boolean value based on whether the
        parent is being added or changed, save the related objects to the
        database. Note that at this point save_form() and save_model() have
        already been called.
        """
        theLogger.info('-----------save_related-----------')
        form.save_m2m()

        for formset in formsets:
            # theLogger.info(formset)
            self.save_formset(request, form, formset, change=change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    inlines = [
        VComponentsInline,
    ]

class VPartsForm(forms.ModelForm):
    # components = forms.ModelChoiceField(label="微组件",queryset=VComponents.objects.all(),required=False)
    cover = forms.CharField(label="图片",widget=MediaBaseWidget(label='',typ='images'),required=False)
    title = forms.CharField(required=False)
    url_obj = forms.CharField(label="链接",widget=MediaBaseWidget(label='',typ='links'),required=False)
    css = forms.CharField(required=False)
    order = forms.IntegerField()
    class Meta:
        model = VParts
        exclude = ()
        show_url = False

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        # self.initial = kwargs.get('initial', None)
        # theLogger.info('-------------Vpage_position_Form----__init__-----------')
        # theLogger.info(self.initial)
        # theLogger.info(instance)
        super().__init__(*args, **kwargs)

class VPartsInline(admin.TabularInline):
    form = VPartsForm
    model = VParts
    # formset = vpos_FormSet
    # template = 'admin/churchs/vpage_tabular.html'

    fields = ('components','cover','title','url_obj','css','order')#,'url_title','url_object','url_id'

    ordering = ('order',)
    extra = 0
    can_delete = True

class VComponentsAdmin(admin.ModelAdmin):
    list_display = ('preview_title','control','create_by','ContentColumn','Media','content','promote')  
    # list_filter = (MediaKindListFilter, 'alioss_video_status')
    fields = ('title','control','ContentColumn','Media','content','add_content')
    readonly_fields = ('add_content',)
    change_form_template ="admin/churchs/change_form_components.html"
    formfield_overrides = {
        VComponents.content: {'widget': CKEditorWidget()},
    }
    inlines = [
        VPartsInline,
    ]
    
    def preview_title(self, obj):
        button_html = """<a  href="/blog/vcomponents/?componentid=%d">%s</a>""" % (obj.id,obj.title)
        return format_html(button_html)
    preview_title.short_description = "预览"
    def promote(self, obj):
        button_html = """<a class="changelink" href="/admin/churchs/vcomponents/%d/change/">编辑</a>""" % obj.id
        return format_html(button_html)
    promote.short_description = "操作"

    def add_content(self, instance):
        # assuming get_full_address() returns a list of strings
        # for each line of the address and you want to separate each
        # line by a linebreak
        if instance.id is None:
            return format_html(
                '''<el-button disabled @click="popupCenter('/media_browse/?from=vcomponent','媒体库',900,600)">{}</el-button>''',
                '批量添加内容,先保存微组件'
            ) 
        else:
            return format_html(
                '''<el-button @click="popupCenter('/media_browse/?type=links&from=vcomponent&vcompid={}','媒体库',900,600)">{}</el-button>''',
                instance.id,
                '批量添加内容'
            )
    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        loger.info(request.__dict__)
        # loger.info(request.POST)

        # data = request.POST
        # count = data.get('vparts_set-TOTAL_FORMS',0)
        # for num in range(0,count-1):
            

        instance = form.save(commit=False)
        loger.info(instance)
        instance.create_by = request.user
        instance.church = request.user.church
        return instance

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                qs = qs.filter(church=request.user.church)
            # loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e


    



    

    