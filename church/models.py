from django.db import models

class Church(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2

    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    time_desc = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_INITED
    )

    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True) 

class Speaker(models.Model):
    church = models.ForeignKey("Church", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    introduction = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True) 

class Meeting(models.Model):
    church = models.ForeignKey("Church", on_delete=models.CASCADE)
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    time = models.DateTimeField
    description = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
class BibleStudy(models.Model):
    church = models.ForeignKey("Church", on_delete=models.CASCADE)
    speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
class BibleStudyComment(models.Model):
    church = models.ForeignKey("Church", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
class Course(models.Model):
    speaker = models.ForeignKey('Speaker', on_delete=models.CASCADE)
    title = models.CharField(u'标题', max_length=32)
    image = models.ImageField(u'图片', upload_to='uploadImages', null=True, blank=True)
    description = models.CharField(u'描述', max_length=255)
    # content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
class Team(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2

    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    
    church = models.ForeignKey("Church", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_INITED
    )
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    
class Donation(models.Model):
    church = models.ForeignKey("Church", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=10, max_digits=12)
    pay_type = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    pay_time = models.DateTimeField(null=True)
    

class User(models.Model):
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=16)
    password = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
