# Generated by Django 2.2.7 on 2019-12-14 11:05

import church.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Church',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='名称')),
                ('code', models.CharField(default='086-010-0001', max_length=32, unique=True, verbose_name='代码')),
                ('description', models.CharField(max_length=255, verbose_name='描叙')),
                ('address', models.CharField(max_length=32, verbose_name='地址')),
                ('promot_cover', models.ImageField(blank=True, null=True, storage=church.storage_backends.PrivateMediaStorage(), upload_to='', verbose_name='海报封面')),
                ('promot_video', models.FileField(blank=True, null=True, storage=church.storage_backends.PrivateMediaStorage(), upload_to='', verbose_name='海报短片')),
                ('status', models.IntegerField(choices=[(1, '正常'), (2, '下线')], default=1, verbose_name='状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '教会',
                'verbose_name_plural': '教会',
            },
        ),
    ]
