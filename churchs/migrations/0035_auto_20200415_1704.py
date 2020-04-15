# Generated by Django 2.2.7 on 2020-04-15 09:04

import church.alioss_storage_backends_v2
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0034_auto_20200407_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=200, verbose_name='标题')),
                ('mime_type', models.CharField(default='', max_length=50, verbose_name='媒体类型')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='sermonseries',
            options={'verbose_name': '专栏系列', 'verbose_name_plural': '专栏系列'},
        ),
        migrations.AddField(
            model_name='sermon',
            name='cover',
            field=models.ImageField(blank=True, null=True, storage=church.alioss_storage_backends_v2.AliyunMediaStorage(), upload_to='', verbose_name='海报封面'),
        ),
    ]
