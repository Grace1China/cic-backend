# Generated by Django 2.2.7 on 2020-07-13 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0062_add_vparts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sermonseries',
            options={'verbose_name': '资料分组', 'verbose_name_plural': '资料分组'},
        ),
        migrations.AlterField(
            model_name='vpagecomponents',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VPage'),
        ),
        migrations.AlterField(
            model_name='vparts',
            name='url',
            field=models.CharField(default='', max_length=250, verbose_name='url'),
        ),
    ]
