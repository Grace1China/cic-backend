# Generated by Django 3.0.1 on 2019-12-24 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0010_auto_20191224_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sermon',
            name='date',
        ),
    ]
