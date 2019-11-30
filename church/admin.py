from django.contrib import admin

from . import models

class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status') 
    search_fields = ('name',)
    fields = ('name', 'description', 'time_desc', 'address', 'status')
    
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('church', 'name', 'title') 
    search_fields = ('name', 'title')
    fields = ('name', 'title', 'introduction')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker') 
    search_fields = ('speaker', 'title')
    fields = ('title', 'speaker', 'image', 'description')
    

class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('church', 'user', 'title') 
    search_fields = ('church', 'user', 'title')
    fields = ('church', 'user', 'title', 'image', 'content')

admin.site.register(models.Church, ChurchAdmin)
admin.site.register(models.Speaker, SpeakerAdmin)
admin.site.register(models.Meeting)
admin.site.register(models.BibleStudy)
admin.site.register(models.BibleStudyComment)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.WeeklyReport, WeeklyReportAdmin)
admin.site.register(models.Team)
admin.site.register(models.Donation)
admin.site.register(models.User)
