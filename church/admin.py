from django.contrib import admin

from . import models
from churchs import models as churchs_md
from church import models as church_md
from users import models as users_md

from api import models as api_md
from ckeditor.widgets import CKEditorWidget
from churchs.models import Media

from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline

class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name','promot_cover', 'status') 
    search_fields = ('name','status')
    fields = ('name', 'code','description', 'address', 'promot_cover', 'promot_video','status','venue','creator','manager')
    def get_changeform_initial_data(self, request):
        return {'creator': request.user}
    


class MediaInline(GenericStackedInline):
    model = Media
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [
        MediaInline,
    ]

    list_display = ('title', 'speaker') 
    search_fields = ('speaker', 'title')
    fields = ('church','title', 'speaker','description','content','price')

    change_form_template ="admin/churchs/sermon_change_form.html"

admin.site.register(church_md.Church, ChurchAdmin)
admin.site.register(models.Course, CourseAdmin)

admin.AdminSite.site_header = '教会平台'
admin.AdminSite.site_title = '教会平台'


