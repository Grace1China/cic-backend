from django.forms import ModelForm
from django import forms
from .models import Media
from .widget import AliVideoWidgetExt,AliOssDirectWidgetExt,MediaBaseWidget
from ckeditor.widgets import CKEditorWidget

import logging
theLogger = logging.getLogger('church.all')

from .models import MediaFile
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


