# Generated by Django 2.2.7 on 2020-02-16 08:38

import churchs.widget
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0025_auto_20200215_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='alioss_audio',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='音频'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_image',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='封面'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_pdf',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='讲义'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_video',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='视频'),
        ),
    ]
