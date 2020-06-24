# Generated by Django 2.2.7 on 2020-06-23 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0052_AddSpeakerNull'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='kind',
            field=models.IntegerField(choices=[(1, '敬拜'), (2, '主持'), (3, '讲道'), (4, '奉献'), (5, '课程'), (6, '视频'), (7, '音频'), (8, '图文'), (9, 'PDF'), (10, '其它')], default=3, verbose_name='媒体种类'),
        ),
    ]
