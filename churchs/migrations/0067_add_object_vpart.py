# Generated by Django 2.2.7 on 2020-07-15 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0066_contentcolumn_addcover'),
    ]

    operations = [
        migrations.AddField(
            model_name='vparts',
            name='url_id',
            field=models.IntegerField(null=True, verbose_name='反射对象id'),
        ),
        migrations.AddField(
            model_name='vparts',
            name='url_object',
            field=models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='反射对象'),
        ),
        migrations.AddField(
            model_name='vparts',
            name='url_title',
            field=models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='标题'),
        ),
        migrations.AlterField(
            model_name='vpagecomponents',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VPage'),
        ),
    ]
