# Generated by Django 2.2.7 on 2020-04-24 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0038_auto_20200424_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='origin_name',
            field=models.CharField(default='', max_length=200, verbose_name='媒体原有文件名'),
        ),
        migrations.AlterField(
            model_name='mediafile',
            name='name',
            field=models.CharField(default='', max_length=200, unique=True, verbose_name='oss存储key GUID'),
        ),
    ]
