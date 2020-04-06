from django.contrib import admin

from . import models
from churchs import models as churchs_md
from church import models as church_md
from users import models as users_md

from api import models as api_md
from ckeditor.widgets import CKEditorWidget
from churchs.models import Media
from parsley.mixins import ParsleyAdminMixin

from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from churchs.forms import MeidaForm2


class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name','promot_cover', 'status') 
    search_fields = ('name','status')
    fields = ('name', 'code','description', 'address', 'promot_cover', 'giving_qrcode', 'promot_video','status','venue','creator','manager')
    def get_changeform_initial_data(self, request):
        return {'creator': request.user}
    


class MediaInline(GenericStackedInline):
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','dist_audio','dist_image','dist_pdf')
    fields = ('alioss_video','alioss_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','alioss_audio','alioss_image','alioss_pdf','content')
    # exclude = ['name']

    extra = 1

class MediaInline1(GenericStackedInline):
    form = MeidaForm2
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_audio','dist_image','dist_pdf')
    fields = (('alioss_video_f','dist_SHD_URL','dist_HD_URL','dist_SD_URL'),'alioss_video_status','alioss_audio_f','alioss_image_f','alioss_pdf_f','content')
   
    extra = 0
    max_num = 4
class CourseAdmin(ParsleyAdminMixin,admin.ModelAdmin):
    inlines = [
        MediaInline1,
    ]

    list_display = ('title', 'teacher') 
    search_fields = ('teacher', 'title')
    fields = ('church','title', 'teacher','description','content','iap_charge','price','price_usd')

    change_form_template ="admin/churchs/sermon_change_form.html"
    
    def get_changeform_initial_data(self, request):
        from churchs.models import Speaker
        spk = Speaker.objects.filter(churchs__in=[request.user.church])[0]
        ret = {'church': request.user.church,'teacher':spk}
        print(ret)
        return ret

admin.site.register(church_md.Church, ChurchAdmin)
admin.site.register(models.Course, CourseAdmin)

admin.AdminSite.site_header = '教会平台'
admin.AdminSite.site_title = '教会平台'


