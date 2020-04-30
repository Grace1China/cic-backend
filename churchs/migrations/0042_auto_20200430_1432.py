# Generated by Django 2.2.7 on 2020-04-30 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0041_mediafile_series_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='video_file_status',
            field=models.IntegerField(choices=[(1, '上传完成'), (2, '正在转码'), (3, '转码发布')], default=1, verbose_name='视频文件状态'),
        ),
        migrations.AddField(
            model_name='mediafile',
            name='video_file_tcinfo',
            field=models.CharField(default='{"image1":"00001.jpg","image2":"00002.jpg","image3":"00003.jpg","sd":"sd.mp4","hd":"hd.mp4","ld":"ld.mp4","audio":"320.mp3"}', max_length=1000, verbose_name='视频转码文件'),
        ),
    ]
