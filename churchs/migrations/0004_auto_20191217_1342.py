# Generated by Django 2.2.7 on 2019-12-17 05:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('churchs', '0003_auto_20191216_1252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weeklyreport',
            name='user',
        ),
        migrations.AddField(
            model_name='weeklyreport',
            name='creator',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='作者'),
        ),
    ]
