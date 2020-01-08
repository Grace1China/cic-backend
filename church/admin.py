from django.contrib import admin

from . import models
from churchs import models as churchs_md
from church import models as church_md
from users import models as users_md

from api import models as api_md
from ckeditor.widgets import CKEditorWidget
# from photos.views import ProgressBarUploadView

class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name','promot_cover', 'status') 
    search_fields = ('name','status')
    fields = ('name', 'code','description', 'address', 'promot_cover', 'promot_video','status','venue','creator','manager')
    def get_changeform_initial_data(self, request):
        return {'creator': request.user}
    
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('church', 'name', 'title') 
    search_fields = ('name', 'title')
    fields = ('name', 'title', 'introduction')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','video', 'speaker') 
    search_fields = ('speaker', 'title')
    fields = ('title', 'speaker', 'image', 'video','description')
    





    


admin.site.register(church_md.Church, ChurchAdmin)
# admin.site.register(churchs_md.Member)
admin.site.register(churchs_md.Team)
admin.site.register(churchs_md.Donation)
admin.site.register(churchs_md.Venue)
# admin.site.register(churchs_md.Sermon,SermonAdmin)
admin.site.register(churchs_md.SermonSeries)
# admin.site.register(churchs_md.userProfile,userProfileAdmin)
# admin.site.register(users_md.CustomUser)

admin.site.register(churchs_md.Speaker, SpeakerAdmin)
admin.site.register(churchs_md.Meeting)
admin.site.register(churchs_md.BibleStudy)
admin.site.register(churchs_md.BibleStudyComment)
admin.site.register(churchs_md.Course, CourseAdmin)
admin.AdminSite.site_header = '教会平台'
admin.AdminSite.site_title = '教会平台'


