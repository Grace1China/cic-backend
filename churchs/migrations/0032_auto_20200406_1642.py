# Generated by Django 2.2.7 on 2020-04-06 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0031_auto_20200404_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sermonseries',
            name='res_path',
            field=models.CharField(blank=True, default='', max_length=250, verbose_name='资源路径'),
        ),
    ]
