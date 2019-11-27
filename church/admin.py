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

admin.site.register(models.Church, ChurchAdmin)
admin.site.register(models.Speaker, SpeakerAdmin)
admin.site.register(models.Meeting)
admin.site.register(models.BibleStudy)
admin.site.register(models.BibleStudyComment)
admin.site.register(models.Course)
admin.site.register(models.Team)
admin.site.register(models.Donation)
admin.site.register(models.User)
