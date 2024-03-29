# Generated by Django 3.0.3 on 2020-03-04 14:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20200304_2210'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('church', '0014_auto_20200229_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, related_name='courses', through='payment.Users_Courses', to=settings.AUTH_USER_MODEL),
        ),
    ]
