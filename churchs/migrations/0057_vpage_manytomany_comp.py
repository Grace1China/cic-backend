# Generated by Django 2.2.7 on 2020-06-28 07:53

import churchs.widget
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0028_church_lord_swipe'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('churchs', '0056_vpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='VComponents',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
                ('control', models.IntegerField(choices=[(1, 'BANNER'), (2, '小图横滑'), (3, '列表'), (4, '富文本')], default=1, verbose_name='控件')),
                ('content', churchs.widget.InlineContentField(blank=True, null=True, verbose_name='内容')),
                ('ContentColumn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.ContentColumn')),
                ('Media', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.Media')),
                ('church', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='church.Church', verbose_name='教会')),
                ('create_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '微组件',
                'verbose_name_plural': '微组件',
            },
        ),
        migrations.CreateModel(
            name='VPageComponents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('components', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VComponents')),
            ],
        ),
        migrations.RemoveField(
            model_name='vpage_position',
            name='ContentColumn',
        ),
        migrations.RemoveField(
            model_name='vpage_position',
            name='Media',
        ),
        migrations.RemoveField(
            model_name='vpage_position',
            name='church',
        ),
        migrations.RemoveField(
            model_name='vpage_position',
            name='create_by',
        ),
        migrations.RemoveField(
            model_name='vpage_position',
            name='vpage',
        ),
        migrations.AddField(
            model_name='columnmedias',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vpage',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vpage',
            name='promote_at',
            field=models.IntegerField(choices=[(1, 'app首页'), (2, '主日信息首页')], default=1, verbose_name='微信面位置'),
        ),
        migrations.DeleteModel(
            name='baseChurchModel',
        ),
        migrations.DeleteModel(
            name='vpage_position',
        ),
        migrations.AddField(
            model_name='vpagecomponents',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VPage'),
        ),
    ]
