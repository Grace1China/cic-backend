# Generated by Django 2.2.7 on 2020-03-27 03:13

import churchs.widget
import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0029_auto_20200309_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='alioss_video',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='视频'),
        ),
        migrations.AlterField(
            model_name='media',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='摘要'),
        ),
    ]
