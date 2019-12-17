from django.conf.urls import url
from django.contrib import admin
from .models import Photo
from .views import ProgressBarUploadView
from django.urls import path, re_path, include

# Register your models here.

class PhotosAdmin(admin.ModelAdmin):
    change_form_template = 'photos/progress_bar_upload/index.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('admin/progress-bar-upload/', self.admin_site.admin_view(ProgressBarUploadView.as_view()))
        ]
        return my_urls + urls

        
admin.site.register(Photo, PhotosAdmin)


# class TemplateAdmin(admin.ModelAdmin):
#     ...
#     change_form_template = 'admin/preview_template.html'

# custom_admin_site.register(models.Template, TemplateAdmin)

# class CustomAdminSite(admin.AdminSite):
  

#     def get_urls(self):
#             urls = super(SermonAdmin, self).get_urls()
#             custom_urls = [
#                 url(r'admin/progress-bar-upload/$', self.admin_view(ProgressBarUploadView.as_view()), name="ProgressBarUploadView"),
#             ]
#             return urls + custom_urls



