# Generated by Django 2.2.7 on 2020-01-07 03:29

import churchs.widget
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0017_auto_20200104_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='alioss_HD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='Aliyun oss 高清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_SD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='Aliyun oss 标清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_SHD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='Aliyun oss 超高清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_audio',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='Aliyun oss 音频'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_image',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='Aliyun oss 封面'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_pdf',
            field=churchs.widget.AliOssDirectField(blank=True, verbose_name='Aliyun oss 讲义'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_HD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='AWS S3 高清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_SD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='AWS S3 标清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_SHD_URL',
            field=models.CharField(blank=True, max_length=400, verbose_name='AWS S3 超高清链接'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_audio',
            field=churchs.widget.S3DirectField(blank=True, verbose_name='AWS S3 音频'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_image',
            field=churchs.widget.S3DirectField(blank=True, verbose_name='AWS S3 封面'),
        ),
        migrations.AlterField(
            model_name='media',
            name='s3_pdf',
            field=churchs.widget.S3DirectField(blank=True, verbose_name='AWS S3 讲义'),
        ),
    ]
