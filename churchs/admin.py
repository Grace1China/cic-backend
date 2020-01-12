from django.contrib import admin
from .models import WeeklyReport, Sermon, Media
from . import models
from ckeditor.widgets import CKEditorWidget


# Register your models here.

class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('title','creator','image', 'pub_time','status')   
    search_fields = ('pub_time', 'title','status')
    fields = ('title','creator','church','image', 'status','content','pub_time')
    readonly_fields = ['pub_time']
    formfield_overrides = {
        models.WeeklyReport.content: {'widget': CKEditorWidget()},
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

admin.site.register(models.WeeklyReport, WeeklyReportAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('church', 'name', 'title') 
    search_fields = ('name', 'title')
    fields = ('name', 'title', 'introduction')

class MediaAdmin(admin.StackedInline):
    model = models.Media
    # form = S3DirectUploadForm
    list_display = ('kind','title','s3_video_status', 'alioss_video_status','content')
    extra = 1
    max_num = 4
    fields = ('kind','title','s3_video','s3_video_status','s3_SHD_URL','s3_HD_URL','s3_SD_URL','s3_audio','s3_image','s3_pdf','alioss_video','alioss_video_status','alioss_SHD_URL','alioss_HD_URL','alioss_SD_URL','alioss_audio','alioss_image','alioss_pdf','content')

    


class SermonAdmin(admin.ModelAdmin):
    model = models.Sermon
    list_display = ('title','user','pub_time','status')
    search_fields = ('pub_time', 'title','status','user')
    fields = ('title','speaker','scripture','series','church','pub_time','status','user')

    inlines = [MediaAdmin]

    change_form_template ="admin/churchs/sermon_change_form.html"
    
admin.site.register(models.Sermon, SermonAdmin)
admin.site.register(models.Team)  
admin.site.register(models.Donation)
admin.site.register(models.Venue)
admin.site.register(models.SermonSeries)

admin.site.register(models.Speaker, SpeakerAdmin)
admin.site.register(models.Meeting)
admin.site.register(models.BibleStudy)
admin.site.register(models.BibleStudyComment)

