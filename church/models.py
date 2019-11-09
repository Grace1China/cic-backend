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
        defautl=STATUS_INITED
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True) 

class Speaker(models.Model):
    church = models.ForeignKey("Church")
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    introduction = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True) 

class Meeting(models.Model):
    church = models.ForeignKey("Church")
    speaker = models.ForeignKey("Speaker")
    name = models.CharField(max_length=32)
    time = models.DateTimeField
    description = models.CharField(max_length=255)
    content = models.TextField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
class BibleStudy(models.Model):
    church = models.ForeignKey("Church")
    speaker = models.ForeignKey("Speaker")
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    content = models.TextField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
class BibleStudyComment(models.Model):
    church = models.ForeignKey("Church")
    user = models.ForeignKey("User")
    content = models.TextField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
class Course(models.Model):
    church = models.ForeignKey("Church")
    speaker = models.ForeignKey("Speaker")
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    content = models.TextField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    

class Team(models.Model):
    STATUS_INITED = 1
    STATUS_OFFLINE = 2

    STATUS_CHOICES = (
        (STATUS_INITED, '正常'),
        (STATUS_OFFLINE, '下线')
    )
    
    church = models.ForeignKey("Church")
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        defautl=STATUS_INITED
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    

class Course(models.Model):
    church = models.ForeignKey("Church")
    speaker = models.ForeignKey("Speaker")
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    content = models.TextField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
class Donation(models,Model):
    church = models.ForeignKey("Church")
    user = models.ForeignKey("User")
    amount = models.DecimalField(decimal_places=10, max_digits=2)
    pay_type = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    pay_time = models.DateTimeField()
    

class User(models.Model):
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=16)
    password = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
