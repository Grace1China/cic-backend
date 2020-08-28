# Generated by Django 2.2.7 on 2020-08-28 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0073_Sermon2Medias_deletekind'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='profile',
            field=models.CharField(max_length=255, null=True, verbose_name='照片'),
        ),
        migrations.AlterField(
            model_name='vpagecomponents',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VPage'),
        ),
    ]
