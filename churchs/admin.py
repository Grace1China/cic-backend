from django.contrib import admin
from .models import WeeklyReport, Sermon, Media
from . import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from .widget import AliVideoWidgetExt
from django.forms import ModelForm,Form



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


class MeidaForm2(forms.ModelForm):
    dist_SHD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="超清视频"),required=False)
    dist_HD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="高清视频"),required=False)
    dist_SD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="流畅视频"),required=False)

    class Meta:
        model = Media
        # exclude = ("geometry", )
        fields = ('alioss_video','dist_SHD_URL','dist_HD_URL','dist_SD_URL','alioss_video_status','alioss_audio','alioss_image','alioss_pdf','content',)
        # widgets = {
        #     dist_HD_URL: AliVideoWidgetExt,
        # }


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {'dist_SHD_URL': instance.dist_SHD_URL,'dist_HD_URL': instance.dist_HD_URL,'dist_SD_URL': instance.dist_SD_URL, }
        return super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # self.instance.dist_SHD_URL = self.cleaned_data['dist_SHD_URL']
        # self.instance.dist_HD_URL = self.cleaned_data['dist_HD_URL']
        # self.instance.dist_SD_URL = self.cleaned_data['dist_SD_URL']
        # if(self.cleaned_data['dist_SHD_URL'])
        import pprint
        pprint.PrettyPrinter(6).pprint('+++++++++++++++form:save')
        pprint.PrettyPrinter(6).pprint(self.instance.alioss_video)
        pprint.PrettyPrinter(6).pprint(self.cleaned_data.get('alioss_video',None))

        if(self.cleaned_data.get('alioss_video',None)!=self.instance.alioss_video):
            self.instance.alioss_SHD_URL = ""
            self.instance.alioss_HD_URL = ""
            self.instance.alioss_SD_URL = ""


        return super().save(*args, **kwargs)

class MediaInline1(GenericStackedInline):
    form = MeidaForm2
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status','alioss_audio','alioss_image','alioss_pdf','content')
   
    extra = 0
    max_num = 4



class MediaInline(GenericStackedInline):
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status',('alioss_audio','alioss_image','alioss_pdf'),'content')
    extra = 0
    max_num = 4
    # formfield_overrides = {
    #     Media.dist_HD_URL: {'widget': AliVideoWidgetExt},
    # }


# class MediaInline(GenericStackedInline):
#     model = Media
    
    

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


