from django.contrib import admin

from . import models
from churchs import models as churchs_md
from ckeditor.widgets import CKEditorWidget

class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name','promot_cover', 'status') 
    search_fields = ('name','status')
    fields = ('name', 'description', 'address', 'promot_cover', 'promot_video','status','vunue')
    
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('church', 'name', 'title') 
    search_fields = ('name', 'title')
    fields = ('name', 'title', 'introduction')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','video', 'speaker') 
    search_fields = ('speaker', 'title')
    fields = ('title', 'speaker', 'image', 'video','description')
    

class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('title','user','image', 'pub_time','status')   
    search_fields = ('pub_time', 'title','status')
    fields = ('title','user','church','image', 'status','content','pub_time')
    readonly_fields = ['pub_time']
    formfield_overrides = {
        churchs_md.WeeklyReport.content: {'widget': CKEditorWidget()},
    }
    # def has_change_permission(self, request, obj=None):
    #     has_class_permission = super(EntryAdmin, self).has_change_permission(request, obj)
    #     if not has_class_permission:
    #         return False
    #     if obj is not None and not request.user.is_superuser and request.user.id != obj.author.id:
    #         return False
    #     return True

    # def queryset(self, request):
    #     if request.user.is_superuser:
    #         return Entry.objects.all()
    #     return Entry.objects.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.church
        obj.save()




admin.site.register(churchs_md.Church, ChurchAdmin)
admin.site.register(churchs_md.WeeklyReport, WeeklyReportAdmin)
admin.site.register(churchs_md.Member)
admin.site.register(churchs_md.Team)
admin.site.register(churchs_md.Donation)
admin.site.register(churchs_md.Venue)




admin.site.register(models.Speaker, SpeakerAdmin)
admin.site.register(models.Meeting)
admin.site.register(models.BibleStudy)
admin.site.register(models.BibleStudyComment)
admin.site.register(models.Course, CourseAdmin)

