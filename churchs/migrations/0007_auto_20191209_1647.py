# Generated by Django 2.2.7 on 2019-12-09 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0006_auto_20191209_1619'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={'verbose_name': '奉献', 'verbose_name_plural': '奉献'},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'verbose_name': '小组', 'verbose_name_plural': '小组'},
        ),
    ]
