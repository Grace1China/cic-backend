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

from churchs.models import MediaFile
class MeidaForm2(forms.ModelForm):
    alioss_video_f = forms.CharField(label="",widget=MediaBaseWidget(label='视频',typ='videos'),required=False)
    alioss_audio_f = forms.CharField(label="",widget=MediaBaseWidget(label='音频',typ='audios'),required=False)
    # alioss_image_f = forms.CharField(label="",widget=AliOssDirectWidgetExt(dest='images',fieldname='alioss_image_f', label='封面'),required=False)
    alioss_image_f = forms.CharField(label="",widget=MediaBaseWidget(label='封面',typ='images'),required=False)
    alioss_pdf_f = forms.CharField(label="",widget=MediaBaseWidget(label='文档',typ='pdfs'),required=False)

    class Meta:
        model = Media
        fields = ('alioss_video_status','content',)
        formfield_overrides = {
            Media.content: {'widget': CKEditorWidget()},
        }


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        # theLogger.info(instance.__dict__)
        if instance:
            kwargs['initial'] = {'alioss_video_f':instance.alioss_video,'alioss_audio_f':instance.alioss_audio,'alioss_image_f':instance.alioss_image,'alioss_pdf_f':instance.alioss_pdf}#'dist_SHD_URL': instance.dist_SHD_URL,'dist_HD_URL': instance.dist_HD_URL,'dist_SD_URL': instance.dist_SD_URL

            theLogger.info({'alioss_video_f':instance.dist_video,'alioss_audio_f':instance.alioss_audio,'alioss_image_f':instance.alioss_image,'alioss_pdf_f':instance.alioss_pdf})#'dist_SHD_URL': instance.dist_SHD_URL,'dist_HD_URL': instance.dist_HD_URL,'dist_SD_URL': instance.dist_SD_URL
        super().__init__(*args, **kwargs)
        # 这里如果没有super init就没有fields,所以super.init要在fields赋值前面


    def save(self, *args, **kwargs):

        self.instance.alioss_video = self.cleaned_data.get('alioss_video_f',None)
        self.instance.alioss_audio = self.cleaned_data.get('alioss_audio_f',None)
        self.instance.alioss_image = self.cleaned_data.get('alioss_image_f',None)
        self.instance.alioss_pdf = self.cleaned_data.get('alioss_pdf_f',None)

        return super().save(*args, **kwargs)

class MediaInline1(GenericStackedInline):
    form = MeidaForm2
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video_f','alioss_audio_f','alioss_image_f','alioss_pdf_f'),'alioss_video_status','content','church') #('alioss_video_f','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),
   
    extra = 1
    max_num = 4
    min_num = 0

    

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
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%d,"%s")'>%d-推广链接</a>""" % (obj.id,'sermon',obj.id)
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

    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        instance.church = request.user.church
        loger.info(self.inlines)
        loger.info(self.inlines[0])
        loger.info(self.inlines[0].get_formset)
        return instance

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