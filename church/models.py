from django.db import models
from church.storage_backends import PrivateMediaStorage
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField




class Speaker(models.Model):
    church = models.ForeignKey("churchs.Church", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    introduction = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True) 
    class Meta:
        verbose_name = "讲员"
        verbose_name_plural = "讲员"

class Meeting(models.Model):
    church = models.ForeignKey("churchs.Church", on_delete=models.CASCADE)
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    time = models.DateTimeField
    description = models.CharField(max_length=255)
    # content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "聚会"
        verbose_name_plural = "聚会"
    
class BibleStudy(models.Model):
    church = models.ForeignKey("churchs.Church", on_delete=models.CASCADE)
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "灵修"
        verbose_name_plural = "灵修"

    
    
class BibleStudyComment(models.Model):
    church = models.ForeignKey("churchs.Church", on_delete=models.CASCADE)
    user = models.ForeignKey("churchs.Member", on_delete=models.CASCADE)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "灵修评论"
        verbose_name_plural = "灵修评论"

    
class Course(models.Model):
    speaker = models.ForeignKey('Speaker', on_delete=models.CASCADE)
    title = models.CharField(u'标题', max_length=32)
    image = models.ImageField(u'图片', upload_to='images', null=True, blank=True)
    description = models.CharField(u'描述', max_length=255)
    # content = models.TextField(null=True, blank=True)
    video = models.FileField(u'视频', storage=PrivateMediaStorage(), null=True, blank=True) 
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"



    
