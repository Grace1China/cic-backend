from django.forms import ModelForm
from django import forms
from .models import Media
from .widget import AliVideoWidgetExt,AliOssDirectWidgetExt
from ckeditor.widgets import CKEditorWidget

class MeidaForm2(forms.ModelForm):
    dist_SHD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="超清视频"),required=False)
    dist_HD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="高清视频"),required=False)
    dist_SD_URL = forms.CharField(label="",widget=AliVideoWidgetExt(dest="destination",label="流畅视频"),required=False)

    alioss_video_f = forms.CharField(label="",widget=AliOssDirectWidgetExt(dest='source',fieldname='alioss_video_f', label='视频'),required=False)
    alioss_audio_f = forms.CharField(label="",widget=AliOssDirectWidgetExt(dest='audios', fieldname='alioss_audio_f',label='音频'),required=False)
    alioss_image_f = forms.CharField(label="",widget=AliOssDirectWidgetExt(dest='images',fieldname='alioss_image_f', label='封面'),required=False)
    alioss_pdf_f = forms.CharField(label="",widget=AliOssDirectWidgetExt(dest='pdfs', fieldname='alioss_pdf_f',label='讲义'),required=False)

    class Meta:
        model = Media
        # exclude = ("geometry", )
        fields = ('alioss_video_status','content',)
        # widgets = {
        #     dist_HD_URL: AliVideoWidgetExt,
        # }
        formfield_overrides = {
            Media.content: {'widget': CKEditorWidget()},
        }


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {'dist_SHD_URL': instance.dist_SHD_URL,'dist_HD_URL': instance.dist_HD_URL,'dist_SD_URL': instance.dist_SD_URL,'alioss_video_f':instance.alioss_video,'alioss_audio_f':instance.alioss_audio,'alioss_image_f':instance.alioss_image,'alioss_pdf_f':instance.alioss_pdf}
        super().__init__(*args, **kwargs)
        # 这里如果没有super init就没有fields,所以super.init要在fields赋值前面
        if instance:
            # kwargs['initial'] = {'dist_SHD_URL': instance.dist_SHD_URL,'dist_HD_URL': instance.dist_HD_URL,'dist_SD_URL': instance.dist_SD_URL, }
            # pprint.PrettyPrinter(6).pprint(instance.__dict__)

            self.fields['dist_SHD_URL'].widget.attrs.update({'class':'show'})
            self.fields['dist_HD_URL'].widget.attrs.update({'class': 'show'})
            self.fields['dist_SD_URL'].widget.attrs.update({'class': 'show'})
        else:
            self.fields['dist_SHD_URL'].widget.attrs.update({'class': 'hide'})
            self.fields['dist_HD_URL'].widget.attrs.update({'class': 'hide'})
            self.fields['dist_SD_URL'].widget.attrs.update({'class': 'hide'})

        # return super().__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        # self.instance.dist_SHD_URL = self.cleaned_data['dist_SHD_URL']
        # self.instance.dist_HD_URL = self.cleaned_data['dist_HD_URL']
        # self.instance.dist_SD_URL = self.cleaned_data['dist_SD_URL']
        # if(self.cleaned_data['dist_SHD_URL'])
        # import pprint
        # pprint.PrettyPrinter(6).pprint('+++++++++++++++form:save')
        # pprint.PrettyPrinter(6).pprint(self.instance.alioss_video)
        # pprint.PrettyPrinter(6).pprint(self.cleaned_data.get('alioss_video',None))

        if(self.cleaned_data.get('alioss_video_f',None)!=self.instance.alioss_video):
            self.instance.alioss_SHD_URL = ""
            self.instance.alioss_HD_URL = ""
            self.instance.alioss_SD_URL = ""

        self.instance.alioss_video = self.cleaned_data.get('alioss_video_f',None)
        self.instance.alioss_audio = self.cleaned_data.get('alioss_audio_f',None)
        self.instance.alioss_image = self.cleaned_data.get('alioss_image_f',None)
        self.instance.alioss_pdf = self.cleaned_data.get('alioss_pdf_f',None)

        return super().save(*args, **kwargs)