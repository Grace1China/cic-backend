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
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from churchs.models import ContentColumn
from church.confs.prod import get_ALIOSS_DESTINATIONS
from django.forms.widgets import HiddenInput

import logging
loger = logging.getLogger('church.all')

class WRForm(forms.ModelForm):
    # creator = forms.ChoiceField (
    #     required=False,
    #     widget=forms.Select(attrs={'readonly': 'readonly','disabled':'disabled'})
    # )
    # church = forms.ChoiceField (
    #     required=False,
    #     widget=forms.Select(attrs={'readonly': 'readonly','disabled':'disabled'})
    # )

    image = forms.CharField(label="",widget=MediaBaseWidget(label='海报',typ='images'),required=False)

    class Meta:
        model = WeeklyReport
        fields = ('title','creator','church','image', 'status','content')

    def __init__(self, *args, **kwargs):
        super(WRForm, self).__init__(*args, **kwargs)
        if self.initial:
            pass
            # when load init from model, when in add page from the admin
            # self.fields['creator'].choices=CustomUser.objects.filter(id=self.initial['creator']).values_list('id','email')
            # self.fields['church'].choices=Church.objects.filter(id=self.initial['church']).values_list('id','name')


# Register your models here.

class WeeklyReportAdmin(admin.ModelAdmin):
    form=WRForm
    list_display = ('title','creator','image', 'pub_time','status','promote')   
    search_fields = ('pub_time', 'title','status')
    #fields = ('title','creator','church','image', 'status','content','pub_time')
    readonly_fields = ['pub_time']
    formfield_overrides = {
        WeeklyReport.content: {'widget': CKEditorWidget()},
    }

    def promote(self, obj):
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,"%s")'>推广链接</a>""" % (obj.id,'tuwen')
        return format_html(button_html)
    promote.short_description = "操作"
    
    def get_changeform_initial_data(self, request):
        return {'creator': request.user.id,'church': request.user.church}

    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        instance.creator = request.user
        instance.church = request.user.church
        return instance

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                qs = qs.filter(Q(church=request.user.church))
                # loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    
admin.site.register(WeeklyReport, WeeklyReportAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title') 
    search_fields = ('churchs','name', 'title')
    fields = ('name', 'churchs','title', 'introduction','profile')
    formfield_overrides = {
        Speaker.profile: {'widget': AliMediaWidgetExt()},
    }



# class MeidaForm_del(forms.Form):
#     name = forms.CharField()
#     url = forms.URLField()
#     comment = forms.CharField(widget=forms.Textarea)

# class MeidaForm1(ModelForm):
#     class Meta:
#         model = Media
#         fields = ('dist_HD_URL',)
#         widgets = {
#             'dist_HD_URL': AliVideoWidgetExt,
#         }

from django.contrib.admin.helpers import InlineAdminFormSet 


class MediaInline1(GenericStackedInline):
    form = MeidaForm2
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video_f','alioss_audio_f','alioss_image_f','alioss_pdf_f'),'alioss_video_status','content') #('alioss_video_f','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),
   
    extra = 1
    max_num = 4
    min_num = 1

from django.contrib.admin.helpers import InlineAdminFormSet

# class MediaInline(GenericStackedInline):
#     model = Media
#     readonly_fields = ('dist_video','dist_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','dist_audio','dist_image','dist_pdf')
#     fields = (('alioss_video','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status',('alioss_audio','alioss_image','alioss_pdf'),'content')
#     extra = 0
#     max_num = 4


from django.db.models.signals import post_save
# from django.dispatch import receiver
from api.serializers import SermonSerializer4API, MediaSerializer4API
import logging
import json
import requests
from django.conf import settings
import pprint


from datetime import datetime




class SereisForm(forms.ModelForm):
    user = forms.ChoiceField (
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly','disabled':'disabled'})
    )
    church = forms.ChoiceField (
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly','disabled':'disabled'})
    )
    
    class Meta:
        model = SermonSeries
        fields = ('title','user','church','pub_time','status','res_path',)
        
        # widgets = {
        #     'user': Fwidgets.Select(attrs={'disabled': True,'class':'daniel'})
        # }
    def clean_user(self):
        # do something that validates your data
        loger.info('--------clean_user-------')
        loger.info(self.__dict__)
        return self.cleaned_data["user"]
    def __init__(self, *args, **kwargs):
        super(SereisForm, self).__init__(*args, **kwargs)
        loger.info(kwargs)
        loger.info(args)
        if self.initial:
            # when load init from model, when add from the admin
            self.fields['user'].choices=CustomUser.objects.filter(id=self.initial['user']).values_list('id','email')
            self.fields['church'].choices=Church.objects.filter(id=self.initial['church']).values_list('id','name')
           
        # self.fields['user'].required = False
        loger.info(self.initial)
        # want initd has the data so when save and load can use it as an filter. 
        # if can not get value when load, then need use instance
        self.fields['res_path'].widget.attrs.update({'readonly':'readonly'})
        # self.fields['user'].widget.attrs.update({'readonly':'readonly','disabled':'disabled'})
        # self.fields['church'].widget.attrs.update({'readonly':'readonly','disabled':'disabled'})
class SermonSeriesAdmin(admin.ModelAdmin):
    model = SermonSeries
    # readonly_fields = ('res_path','user','church')
    list_display = ('title','church','res_path','status')
    search_fields = ('pub_time', 'title','status','user')
    # fields = ('title','user','church','pub_time','status','res_path')
    # exclude = ('user','church')

    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size':'20'})},
    #     models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    # }

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            qs = qs.filter(church=request.user.church)
            loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    
    # def clean():

    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        instance.user = request.user
        loger.info(request.user.church)
        instance.church = request.user.church
        return instance
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = SereisForm
        return super().get_form(request, obj, **kwargs)
    
    # def get_readonly_fields(self, request, obj=None):
    #     return ['res_path','user','church']

    def get_changeform_initial_data(self, request):
        rd =  {
            'title': '' ,
            'user':request.user.id,
            'church':request.user.church.id,
            'pub_time':datetime.now(),
            'status':SermonSeries.STATUS_OPEN,
            'res_path':'--empty--'
        }   
        loger.info(rd)
        return rd

# from .models import test1
# class test1Admin (admin.ModelAdmin):
#     model = test1
#     list_display = ('image',)
#     formfield_overrides = {
#         test1.image: {'widget': MediaBaseWidget()},
#     }




# admin.site.register(churchs_models.test1,test1Admin)

# class VenueAdmin(admin.ModelAdmin):





# admin.site.register(churchs_models.Team)  
# admin.site.register(churchs_models.Donation)
# admin.site.register(churchs_models.Venue)
admin.site.register(churchs_models.SermonSeries,SermonSeriesAdmin)

# admin.site.register(churchs_models.Speaker, SpeakerAdmin)
# admin.site.register(churchs_models.Meeting)
# admin.site.register(churchs_models.BibleStudy)
# admin.site.register(churchs_models.BibleStudyComment)
# admin.site.register(churchs_models.Media)

from churchs.admins.admin_Content import MediaVideoAdmin    
admin.site.register(churchs_models.Media, MediaVideoAdmin)


from churchs.admins.admin_ContentColumn import ContentColumnAdmin
admin.site.register(churchs_models.ContentColumn,ContentColumnAdmin)

from churchs.admins.admin_Sermon import SermonAdmin
admin.site.register(churchs_models.Sermon, SermonAdmin)

from churchs.admins.admin_Vpage import VPageAdmin,VComponentsAdmin
admin.site.register(churchs_models.VPage,VPageAdmin)
admin.site.register(churchs_models.VComponents,VComponentsAdmin)




