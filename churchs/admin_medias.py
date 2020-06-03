from django.contrib import admin
from .models import WeeklyReport, Sermon, Media,SermonSeries,Speaker
from . import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .widget import AliVideoWidgetExt
from django.forms import ModelForm,Form
from .widget import S3DirectField,AliOssDirectField,AliOssDirectWidgetExt,AliMediaWidgetExt,MediaBaseWidget
from .forms import MeidaForm2
from users.models import CustomUser
from church.models import Church
from django.utils.html import format_html
from django import forms
from django.db.models import Q
from django.forms import widgets as Fwidgets
from django.forms import fields

import logging
loger = logging.getLogger('church.all')



class MediaVideoForm_del(forms.ModelForm):
    image = forms.CharField(label="",widget=MediaBaseWidget(label='海报',typ='images'),required=False)

    class Meta:
        model = churchs_models.Media
        fields = ('title','creator','church','image', 'status','content')

    def __init__(self, *args, **kwargs):
        super(WRForm, self).__init__(*args, **kwargs)
        if self.initial:
            pass
            # when load init from model, when in add page from the admin
            # self.fields['creator'].choices=CustomUser.objects.filter(id=self.initial['creator']).values_list('id','email')
            # self.fields['church'].choices=Church.objects.filter(id=self.initial['church']).values_list('id','name')

class MediaVideoForm(forms.ModelForm):
  
    alioss_video = forms.CharField(label="",widget=MediaBaseWidget(label='视频',typ='videos'),required=False)
    alioss_image = forms.CharField(label="",widget=MediaBaseWidget(label='封面',typ='images'),required=False)

    class Meta:
        model = churchs_models.Media
        fields = ('title','alioss_video','alioss_image','alioss_video_status','content',)
        formfield_overrides = {
            Media.content: {'widget': CKEditorWidget()},
        }

    def __init__(self, *args, **kwargs):
        super(MediaVideoForm,self).__init__(*args, **kwargs)

class MediaVideoAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    list_display = ('title','kind', 'alioss_video_status','promote')  
    fieldsets = (
        (None, {
            'fields': ('title','kind','alioss_video_status','alioss_video','alioss_image')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('content'),
        }),
    ) 
    # search_fields = ('pub_time', 'title','status')
    #fields = ('title','creator','church','image', 'status','content','pub_time')
    # readonly_fields = ['pub_time']
    formfield_overrides = {
        churchs_models.Media.content: {'widget': CKEditorWidget()},
    }

    def promote(self, obj):
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,"%s")'>推广链接</a>""" % (obj.id,'touvideo')
        return format_html(button_html)
    promote.short_description = "操作"
    
    def get_changeform_initial_data(self, request):
        return {'alioss_video_status': churchs_models.Media.MEDIA_OTHER}

    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        # instance.creator = request.user
        # instance.church = request.user.church
        return instance
    

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = MediaVideoForm
        return super().get_form(request, obj, **kwargs)

    # def get_queryset(self, request):
    #     try:
    #         qs = super().get_queryset(request)
    #         if not request.user.is_superuser:
    #             qs = qs.filter(Q(church=request.user.church))
    #             # loger.info(qs)
    #         return qs
    #     except Exception as e:
    #         import traceback
    #         loger.exception('There is and exceptin',exc_info=True,stack_info=True)
    #         raise e
    
admin.site.register(churchs_models.Media, MediaVideoAdmin)
