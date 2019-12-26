from django.contrib import admin
from .models import WeeklyReport, Sermon, Media
from ckeditor.widgets import CKEditorWidget


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


# class SermonAdmin(admin.ModelAdmin):
#     list_display = ('title','user','cover','pub_time','status')
#     search_fields = ('pub_time', 'title','status','user')
#     fields = ('title','creator','church','image', 'status','content','pub_time')

class MediaAdmin(admin.StackedInline):
    model = Media
    # form = S3DirectUploadForm
    list_display = ('kind','title','video', 'image','pdf', 'content')
    extra = 4
    fields = ('kind','title','video','video_status','SHD_URL','HD_URL','SD_URL','audio', 'image','pdf', 'content')

    
 
 
# admin.site.register(Media, MediaAdmin)

   
# class pdfstoreInline(admin.StackedInline):
#     model = pdfstore
#     extra = 1

class SermonAdmin(admin.ModelAdmin):
    model = Sermon
    list_display = ('title','user','pub_time','status')
    search_fields = ('pub_time', 'title','status','user')
    fields = ('title','speaker','scripture','series','church','pub_time','status','user')

    inlines = [MediaAdmin]
    
admin.site.register(Sermon, SermonAdmin)

