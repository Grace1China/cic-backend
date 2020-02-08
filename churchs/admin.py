from django.contrib import admin
from .models import WeeklyReport, Sermon, Media
from . import models
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline



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
    list_display = ('name', 'title') 
    search_fields = ('churchs','name', 'title')
    fields = ('name', 'churchs','title', 'introduction')




class MediaInline(GenericStackedInline):
    model = Media
    readonly_fields = ('dist_video','dist_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','dist_audio','dist_image','dist_pdf')
    fields = ('alioss_video','alioss_video_status','dist_SHD_URL','dist_HD_URL','dist_SD_URL','alioss_audio','alioss_image','alioss_pdf','content')
    extra = 0
    max_num = 4

# class MediaInline(GenericStackedInline):
#     model = Media
    
    

class SermonAdmin(admin.ModelAdmin):
    inlines = [
        MediaInline,
    ]

    model = models.Sermon
    list_display = ('title','user','pub_time','status')
    search_fields = ('pub_time', 'title','status','user')
    fields = ('title','speaker','scripture','series','church','pub_time','status','user')


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
admin.site.register(models.Media)


