# Generated by Django 2.2.7 on 2020-05-22 02:28

import churchs.widget
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('churchs', '0043_auto_20200430_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='test1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', churchs.widget.MediaBaseField(blank=True, max_length=400, verbose_name='封面')),
            ],
        ),
        migrations.AddField(
            model_name='venue',
            name='createdby',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_image',
            field=churchs.widget.MediaBaseField(blank=True, max_length=400, verbose_name='封面'),
        ),
        migrations.AlterField(
            model_name='media',
            name='alioss_video',
            field=churchs.widget.MediaBaseField(blank=True, max_length=400, verbose_name='视频'),
        ),
    ]
