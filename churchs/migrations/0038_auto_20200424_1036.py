# Generated by Django 2.2.7 on 2020-04-24 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0037_auto_20200423_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='name',
            field=models.CharField(default='', max_length=200, unique=True, verbose_name='oss存储key'),
        ),
    ]
