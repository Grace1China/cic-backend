# Generated by Django 2.2.7 on 2020-01-12 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0020_auto_20200112_1104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='owner',
        ),
    ]