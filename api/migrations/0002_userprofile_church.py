# Generated by Django 2.2.7 on 2019-12-07 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0005_church_code'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='church',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='churchs.Church'),
        ),
    ]
