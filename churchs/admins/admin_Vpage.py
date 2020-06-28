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
from churchs.models.vpage import VComponents,VPageComponents

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
    components = forms.ModelChoiceField(label="微组件",queryset=VComponents.objects.all(),required=False)
    church = forms.ModelChoiceField(label="教会",queryset=Church.objects.all(),required=False)
    create_by = forms.ModelChoiceField(label="用户",queryset=CustomUser.objects.all(),required=False)
    # content = forms.Field(label="富文本", required=False)

    class Meta:
        model = VComponents
        exclude = ()

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self.initial = kwargs.get('initial', None)
        theLogger.info('-------------Vpage_position_Form----__init__-----------')
        theLogger.info(self.initial)
        theLogger.info(instance)
        super().__init__(*args, **kwargs)
        


from django.forms import models
class vpos_FormSet(models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(vpos_FormSet, self).__init__(*args, **kwargs)

        theLogger.info(kwargs['instance'])
        self.initial = theLogger.info(kwargs['initial'])
        instance = kwargs['instance']
        # for form in self.forms:
        # Check that the data doesn't already exist
        if not instance.vpage_position_set.filter(vpage=instance.id):
            theLogger.info(kwargs['initial'])
            self.initial = kwargs['initial']
            self.extra += len(self.initial)

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

class vpos_Inline(admin.TabularInline):
    # form = Vpage_position_Form
    model = VPageComponents
    # formset = vpos_FormSet
    template = 'admin/churchs/vpage_tabular.html'
    # fields = ('id','control','ContentColumn','Media','content','church','create_by')
    ordering = ('order',)
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
    
    extra = 0
    can_delete = True
    # max_num = 4
    # min_num = 1

   

class VpageAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)


    list_display = ('title','name', 'pub_time','promote_at','status','promote')  
    # list_filter = (MediaKindListFilter, 'alioss_video_status')
    fields = ('title','name', 'pub_time','promote_at','status')
    
    change_form_template ="admin/churchs/change_form_vpage.html"

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
        vpos_Inline,
    ]



class VComponents(admin.ModelAdmin):
    list_display = ('title','name', 'pub_time','promote_at','status','promote')  
    # list_filter = (MediaKindListFilter, 'alioss_video_status')
    fields = ('title','name', 'pub_time','promote_at','status')
    formfield_overrides = {
        churchs_models.Media.content: {'widget': CKEditorWidget()},
    }



    

    