# Generated by Django 2.2.7 on 2019-12-18 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0005_auto_20191217_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyreport',
            name='status',
            field=models.IntegerField(choices=[(1, '草稿'), (2, '发布'), (3, '测试')], default=1, verbose_name='状态'),
        ),
    ]
