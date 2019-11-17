from django.contrib import admin

from . import models

# class ChurchAdmin(admin.ModelAdmin):
#     fields = ('name', 'description', 'time_desc', 'address', 'status')

admin.site.register(models.Church)
admin.site.register(models.Speaker)
admin.site.register(models.Meeting)
admin.site.register(models.BibleStudy)
admin.site.register(models.BibleStudyComment)
admin.site.register(models.Course)
admin.site.register(models.Team)
admin.site.register(models.Donation)
admin.site.register(models.User)
