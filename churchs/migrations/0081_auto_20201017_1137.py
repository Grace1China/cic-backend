# Generated by Django 2.2.7 on 2020-10-17 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0080_auto_20201017_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentcolumn',
            name='parentCol',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.ContentColumn', verbose_name='父专栏'),
        ),
    ]
