# Generated by Django 2.2.7 on 2020-08-16 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('churchs', '0069_add_sermon_medias'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SermonMedias',
            new_name='Sermon2Medias',
        ),
        migrations.AlterField(
            model_name='vpagecomponents',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='churchs.VPage'),
        ),
    ]
