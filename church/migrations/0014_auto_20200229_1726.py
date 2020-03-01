# Generated by Django 3.0.3 on 2020-02-29 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0013_auto_20200216_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price_usd',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='美元价格'),
        ),
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='人民币价格'),
        ),
    ]
