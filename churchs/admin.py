from django.contrib import admin
from .models import WeeklyReport, Sermon, Media
from . import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .widget import AliVideoWidgetExt
from django.forms import ModelForm,Form
from .widget import S3DirectField,AliOssDirectField,AliOssDirectWidgetExt
from .forms import MeidaForm2




# Register your models here.

class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('title','creator','image', 'pub_time','status')   
    search_fields = ('pub_time', 'title','status')
    fields = ('title','creator','church','image', 'status','content','pub_time')
    readonly_fields = ['pub_time']
    formfield_overrides = {
        WeeklyReport.content: {'widget': CKEditorWidget()},
    }


    # def has_change_permission(self, request, obj=None):
    #     has_class_permission = super(EntryAdmin, self).has_change_permission(request, obj)
    #     if not has_class_permission:
    #         return False
    #     if obj is not None and not request.user.is_superuser and request.user.id != obj.author.id:
    #         return False
    #     return True

    def queryset(self, request):
        # qs = 
        if request.user:
            qs = super().get_queryset(request)
            qs.filter(creator=request.user)
        else:
            return  super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.church
        obj.save()

admin.site.register(WeeklyReport, WeeklyReportAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title') 
    search_fields = ('churchs','name', 'title')
    fields = ('name', 'churchs','title', 'introduction')

from django import forms
class MeidaForm(forms.Form):
    name = forms.CharField()
    url = forms.URLField()
    comment = forms.CharField(widget=forms.Textarea)

# class MeidaForm1(ModelForm):
#     class Meta:
#         model = Media
#         fields = ('dist_HD_URL',)
#         widgets = {
#             'dist_HD_URL': AliVideoWidgetExt,
#         }




class MediaInline1(GenericStackedInline):
    form = MeidaForm2
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video_f','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status','alioss_audio_f','alioss_image_f','alioss_pdf_f','content')
   
    extra = 0
    max_num = 4



class MediaInline(GenericStackedInline):
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status',('alioss_audio','alioss_image','alioss_pdf'),'content')
    extra = 0
    max_num = 4


from django.db.models.signals import post_save
# from django.dispatch import receiver
from api.serializers import SermonSerializer4API, MediaSerializer4API
import logging
import json
import requests
from django.conf import settings
import pprint


def mainsite_api_v1_makesermon(sender,instance, **kwargs):
    try:

        loger = logging.getLogger('church.all')
        inst1 = Sermon.objects.all().get(id=instance.id)
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
            'published':0 if dt["status"]== Sermon.STATUS_DRAFT else 0,
            'ministry':dt["church"]["id"], 
            'video_link':dt["medias"][0]['SHD_URL'] if len(dt["medias"])>0 else '', 
            'teacher':dt["speaker"]["id"], 
            'imagelrg': '%s?x-oss-process=image/resize,m_fixed,h_100,w_100' % dt["medias"][0]['image'] if len(dt["medias"])>0 else '',
            'audio_link': dt["medias"][0]['audio'] if len(dt["medias"])>0 else '',
            'slides_link': dt["medias"][0]['pdf'] if len(dt["medias"])>0 else '',
            'notes_link': dt["medias"][0]['pdf'] if len(dt["medias"])>0 else ''
        }

        loger.info(data)

        if sender.status == Sermon.STATUS_DRAFT:
            pass
        else:
            r = None
            if settings.DEBUG:
                r = requests.post(settings.MAINSITE_API_V1['DEVELOPMENT'], json=json.dumps(data))
            else:
                r = requests.post(settings.MAINSITE_API_V1['DEBUG'], json=json.dumps(data))
            loger.info(pprint.PrettyPrinter(6).pprint(r))
            if r.errCode != '0':
                raise Exception('There is an err\n%s' % r.sysErrMsg)
            
    except Exception as e:
        # pprint.PrettyPrinter(4).pprint(e.__traceback__)
        import traceback
        import sys
        loger = logging.getLogger('church.all')
        loger.exception('There is and exceptin',exc_info=True,stack_info=True)
        # do_something_else()

post_save.connect(mainsite_api_v1_makesermon, sender=Sermon)
    
from datetime import datetime

class SermonAdmin(admin.ModelAdmin):
    inlines = [
        MediaInline1,
    ]

    model = Sermon
    list_display = ('title','user','pub_time','status')
    search_fields = ('pub_time', 'title','status','user')
    fields = ('title','speaker','scripture','series','church','pub_time','status','user')

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if not isinstance(inline, MediaInline) or obj is not None:
                yield inline.get_formset(request, obj), inline

    change_form_template ="admin/churchs/sermon_change_form.html"

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
    
admin.site.register(churchs_models.Sermon, SermonAdmin)
admin.site.register(churchs_models.Team)  
admin.site.register(churchs_models.Donation)
admin.site.register(churchs_models.Venue)
admin.site.register(churchs_models.SermonSeries)

admin.site.register(churchs_models.Speaker, SpeakerAdmin)
admin.site.register(churchs_models.Meeting)
admin.site.register(churchs_models.BibleStudy)
admin.site.register(churchs_models.BibleStudyComment)
admin.site.register(churchs_models.Media)


