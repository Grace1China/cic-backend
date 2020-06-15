from django.contrib import admin
from .models import WeeklyReport, Sermon, Media,SermonSeries,Speaker
from . import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .widget import AliVideoWidgetExt
from django.forms import ModelForm,Form
from .widget import S3DirectField,AliOssDirectField,AliOssDirectWidgetExt,AliMediaWidgetExt,MediaBaseWidget,MediaContentWidget
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
   
    extra = 0
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

class SermonAdmin(admin.ModelAdmin):
    inlines = [
        MediaInline1,
    ]

    model = Sermon
    list_display = ('title','user','pub_time','status','promote')
    search_fields = ('pub_time', 'title','status','user')
    fields = ('title','cover','speaker','scripture','series','church','pub_time','status','user')

    # def get_formsets_with_inlines(self, request, obj=None):
    #     for inline in self.get_inline_instances(request, obj):
    #         # hide MyInline in the add view
    #         if not isinstance(inline, MediaInline) or obj is not None:
    #             yield inline.get_formset(request, obj), inline

    change_form_template ="admin/churchs/sermon_change_form.html"

    
    def promote(self, obj):
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,%s)'>推广链接</a>""" % (obj.id,'sermon')
        return format_html(button_html)
    promote.short_description = "操作"

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
             
    def get_changeform_initial_data(self, request):
        return {
            'title': datetime.now() ,
            'speaker': churchs_models.Speaker.objects.all().filter(churchs=request.user.church)[0] if len(churchs_models.Speaker.objects.all().filter(churchs=request.user.church))>0 else None,
            'scripture' :'',
            'series':churchs_models.SermonSeries.objects.all().filter(church=request.user.church)[0] if len(churchs_models.SermonSeries.objects.all().filter(church=request.user.church))>0 else None,
            'church':request.user.church,
            'pub_time': datetime.now() ,
            'status':Sermon.STATUS_DRAFT,
            'user':request.user
        }

    # actions = ['mainsite_api_v1_makesermon']

    def mainsite_api_v1_makesermon(self, request, queryset):
        try:


            loger.info(request)
            for qr in queryset:
                inst1 = Sermon.objects.all().get(id=qr.id)
                # {'_state': <django.db.models.base.ModelState object at 0x00000187B7344BA8>, 'id': 63, 'church_id': 2, 'user_id': 20, 'title': 'ims/IMS20200301.mp4', 'speaker_id': 192, 'scripture': 'empty', 'series_id': None, 'create_time': datetime.datetime(2020, 3, 2, 9, 43, 52, 231422, tzinfo=<UTC>), 'update_time': datetime.datetime(2020, 3, 2, 12, 43, 51, 112888, tzinfo=<UTC>), 'pub_time': datetime.datetime(2020, 3, 2, 17, 43, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>), 'status': 1}
                # loger.info(instance.id)
                SermonSerializer4API
                szSermon = SermonSerializer4API(inst1)
                loger.info("------------------mainsite_api_v1_makesermon--1--------------------------")
                loger.info(inst1)
                loger.info(szSermon.data.__dict__)
                dt = szSermon.data

                # loger.info(repr(szSermon))
                loger.info("------------------mainsite_api_v1_makesermon--2--------------------------")


                # loger.info(szSermon.__dict__)

                data = {'study_name':dt["title"],
                    'study_date':dt["pub_time"], 
                    'publish_up':dt["pub_time"],
                    'published':0 if dt["status"]== Sermon.STATUS_DRAFT else 1,
                    'ministry':dt["church"]["id"], 
                    'video_link':dt["medias"][0]['SHD_URL'] if len(dt["medias"])>0 else '', 
                    'teacher':dt["speaker"]["id"], 
                    'imagelrg': '%s' % dt["medias"][0]['image'] if len(dt["medias"])>0 else '',
                    'audio_link': dt["medias"][0]['audio'] if len(dt["medias"])>0 else '',
                    'slides_link': dt["medias"][0]['pdf'] if len(dt["medias"])>0 else '',
                    'notes_link': dt["medias"][0]['pdf'] if len(dt["medias"])>0 else ''}

                data['imagelrg'] = (data['imagelrg'] if data['imagelrg'] != '' else szSermon.data['church']['promot_cover'])
                loger.info(data)

                if dt['status'] == Sermon.STATUS_DRAFT:
                    pass
                else:
                    r = None
                    r = requests.post(settings.MAINSITE_API_V1, json=json.dumps(data))
                    loger.info(r.__dict__)
                    if eval(r.content).errCode != '0':
                        raise Exception('There is an err\n%s' % r.sysErrMsg)
                    
        except Exception as e:
            # pprint.PrettyPrinter(4).pprint(e.__traceback__)
            import traceback
            import sys
            loger = logging.getLogger('church.all')
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)

        
    mainsite_api_v1_makesermon.short_description = "make sermon in mainsite"


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




admin.site.register(churchs_models.Sermon, SermonAdmin)
# admin.site.register(churchs_models.Team)  
# admin.site.register(churchs_models.Donation)
# admin.site.register(churchs_models.Venue)
admin.site.register(churchs_models.SermonSeries,SermonSeriesAdmin)

# admin.site.register(churchs_models.Speaker, SpeakerAdmin)
# admin.site.register(churchs_models.Meeting)
# admin.site.register(churchs_models.BibleStudy)
# admin.site.register(churchs_models.BibleStudyComment)
# admin.site.register(churchs_models.Media)



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


class MediaKindListFilter(admin.SimpleListFilter):

    title = _('内容类型')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'kind'

    def lookups(self, request, model_admin):
        return (
            (6, _('视频')),
            (7, _('音频')),
            (8, _('图文')),
        )

    def queryset(self, request, queryset):
        return queryset.filter(kind=self.value())
class MediaVideoAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)
    list_display = ('title','kind', 'alioss_video_status','promote')  
    list_filter = (MediaKindListFilter, 'alioss_video_status')
    fieldsets = (
        (None, {
            'fields': ('title','kind','alioss_video_status','alioss_video','alioss_image')
        },),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('content',),
        },),
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
        instance.user = request.user
        instance.church = request.user.church
        return instance
    

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = MediaVideoForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            request.GET = request.GET.copy()
            fp = request.GET.pop('frompage', [])
            columnid = request.GET.pop('columnid', [])

            if (len(fp) == 1):
                self.frompage = fp[0]
            if (len(columnid) == 1):
                self.columnid = columnid[0]
            if not request.user.is_superuser:
                qs = qs.filter(Q(church=request.user.church) |  Q(kind__in=[churchs_models.Media.MEDIA_VIDEOS,churchs_models.Media.MEDIA_AUDIOS,churchs_models.Media.MEDIA_TUWEN]))
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    frompage = ''
    columnid = 0
    
    actions = ['add_to_column']
    def add_to_column(self, request, queryset):
        # from django.contrib.contenttypes.fields import GenericForeignKey
        # from django.contrib.contenttypes.models import ContentType
        # ctype = ContentType.objects.get(app_label='churchs', model='contentcolumn')
        # Media.objects.update(content_object=comment, activity_type=Activity.LIKE, user=request.user)

        from django.http import HttpResponse
        col = ContentColumn.objects.get(id=self.columnid)
        for m in queryset.all():
            col.medias.add(m)
        col.save()
        response = HttpResponse(content_type="text/html")
        response.write('''<script>
            window.opener.window.formVue.loadForm();
            window.close();
        </script>''')
        return response


    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.frompage != 'content_column' and 'add_to_column' in actions:
            del actions['add_to_column']
        return actions

    # add_to_column.allowed_permissions = ('加入专栏',)
    add_to_column.short_description = "加入专栏"
    
admin.site.register(churchs_models.Media, MediaVideoAdmin)

from churchs.models import ColumnMedias
class ColumnMediasForm(forms.ModelForm):
    # Media_cover = forms.CharField(label="",widget=MediaContentWidget(label='封面',typ='images'),required=False)
    # Media_title = forms.CharField(label="",required=False)
    # Media = forms.CharField(label="",required=False)
    # class Meta:
    #     model = churchs_models.Media
    #     fields = ('title','alioss_video','alioss_image','alioss_video_status','content',)
    #     formfield_overrides = {
    #         Media.content: {'widget': CKEditorWidget()},
    #     }
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
    readonly_fields = ('Media_cover','Media_link',)
    
    extra = 0
    # max_num = 4
    # min_num = 1

    def Media_cover(self, instance):
        # assuming get_full_address() returns a list of strings
        return format_html(
            '''<img src="{}" @click="popupCenter('/admin/churchs/media/?mediaid={}','媒体库',900,600)">''',
            'http://%s/%s' % (get_ALIOSS_DESTINATIONS(typ='images')['redirecturl'], instance.Media.alioss_image),
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
    # short_description functions like a model field's verbose_name
    Media_link.short_description = ""
    

class ContentColumnAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)
    
    change_form_template ="admin/churchs/change_form_content.html"

    list_display = ('title','user','pub_time','status')  
    fieldsets = (
        (None, {
            'fields': ('title','pub_time','status','add_content')
        },),
        # ('Advanced options', {
        #     'classes': ('collapse',),
        #     'fields': ('content',),
        # },),
    ) 
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
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e

    def get_changeform_initial_data(self, request):
        return {'user': request.user.id,'church': request.user.church,'status': churchs_models.ContentColumn.STATUS_CLOSE}

    def save_form(self, request, form,change):
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
        

        # def get_form(self, request, obj=None, **kwargs):
        #     kwargs['form'] = MediaVideoForm
        #     return super().get_form(request, obj, **kwargs)

admin.site.register(churchs_models.ContentColumn,ContentColumnAdmin)



